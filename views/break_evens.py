import time
import re
import copy

from flask import jsonify, request, render_template, send_file
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app import app, bcrypt, settings, db
from lib.impact import surveys
from lib.email import send_reset_password_email
import utils as utils
import models as m


@app.route('/be/sankey', methods=['GET'])
@jwt_required
def get_a_sankey():
    # user = m.User.query.filter_by(email='tester@futurefitbusiness.org').first()
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    bea = m.BreakEvenAssessment.query.filter_by(company_id=user.company.id).first()
    convert_risk = {
        'Unlikely': 0,
        'Low': 1,
        'Moderate': 2,
        'High': 3
    }

    be_nodes = []
    sdg_nodes = []
    links = []

    for goal in bea.goals:
        sdgs = utils.sdg_links[goal.code]
        # print(goal.code)
        for sdg in sdgs:
            risk_value = convert_risk[goal.risk]
            if risk_value > 0:
                be_nodes.append(goal.code)
                sdg_nodes.append(sdg)
                sdg_link_text = surveys.sdg_to_be_tooltips[goal.code].get(str(sdg), '')
                # print(goal.code)
                links.append({
                    'target': sdg,
                    'source': goal.code,
                    'sdg': sdg,
                    'sdg_text': utils.sdgs[str(sdg)]['title'],
                    'code': goal.code,
                    'be_text': surveys.be_text_lookup['break_evens'][goal.code]['long_name'],
                    'value': risk_value,
                    'risk': goal.risk,
                    'sdg_link_text': sdg_link_text,
                })

    goal_risks = {goal.code: goal.risk for goal in bea.goals}
    # format nodes, plus add ids
    be_nodes = list(set(be_nodes))
    sdg_nodes = list(set(sdg_nodes))

    sortings = [
        be_risk_sdg_number(be_nodes, sdg_nodes, copy.deepcopy(links), convert_risk, goal_risks),
        be_number_sdg_number(be_nodes, sdg_nodes, copy.deepcopy(links)),
        be_number_sdg_risk(be_nodes, sdg_nodes, copy.deepcopy(links), convert_risk, goal_risks),
    ]

    return jsonify({
        'sortings': sortings,
        'goal_risks': goal_risks,
    })

def be_risk_sdg_number(be_nodes, sdg_nodes, links, convert_risk, goal_risks):
    be_nodes = sorted(be_nodes, key=lambda x: (convert_risk[goal_risks[x]],), reverse=True)
    sdg_nodes = sorted(sdg_nodes)
    res = finish_linking_nodes(be_nodes, sdg_nodes, links)
    res['name'] = 'Break-Even risk (High-Low) / SDG numerical (default)'
    res['id'] = 0
    return res

def be_number_sdg_number(be_nodes, sdg_nodes, links):
    be_nodes = sorted(be_nodes)
    sdg_nodes = sorted(sdg_nodes)
    res = finish_linking_nodes(be_nodes, sdg_nodes, links)
    res['name'] = 'Break-Even numerical / SDG numerical'
    res['id'] = 1
    return res


def be_number_sdg_risk(be_nodes, sdg_nodes, links, convert_risk, goal_risks):
    be_nodes = sorted(be_nodes)
    sdg_risks = {}
    for link in links:
        sdg = link['sdg']
        if sdg not in sdg_risks:
            sdg_risks[sdg] = 0
        sdg_risks[sdg] += link['value']
    # print('orig')
    # print(sdg_risks)
    # sdg_risks = sorted(sdg_risks, key=lambda x: sdg_risks[x])
    # print('orig sort')
    # print(sdg_risks)
    sdg_nodes = sorted(sdg_nodes, key=lambda x: sdg_risks[x], reverse=True)
    # print('nodes sort')
    # print(sdg_nodes)
    res = finish_linking_nodes(be_nodes, sdg_nodes, links)
    res['name'] = 'Break-Even numerical / SDG risk (High-Low)'
    res['id'] = 2
    return res



def finish_linking_nodes(be_nodes, sdg_nodes, links):
    nodes = []
    id = 0
    lookup = {}
    all_nodes = be_nodes + sdg_nodes

    for node in all_nodes:
        nodes.append({'name': node})
        lookup[node] = id
        id += 1

    # replace values with the node ids
    for link in links:
        source = link['source']

        # print(source)
        link['source'] = lookup[source]
        target = link['target']
        link['target'] = lookup[target]


    return {
        'nodes': nodes,
        'links': links
    }


@app.route('/be', methods=['GET'])
@jwt_required
def get_all_break_evens():
    # user = m.User.query.filter_by(email='tester@futurefitbusiness.org').first()
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    bea = m.BreakEvenAssessment.query.filter_by(company_id=user.company.id).first()
    if not bea:
        bea = utils.setup_heatmap_template_questions(user)

    res = {}
    goal_ids = [goal.id for goal in bea.goals]
    all_questions = surveys.heatmap_template_questions['questions']
    all_answers = m.BreakEvenAssessmentAnswer.query.filter(m.BreakEvenAssessmentAnswer.goal_id.in_(goal_ids)).all()
    json_all_answers = {}

    for answer in all_answers:
        json_all_answers[answer.code] = {
            'value': answer.value,
            'id': answer.id,
        }

    for goal in bea.goals:
        code = goal.code
        sdgs = utils.sdg_links[code]
        goal_survey = surveys.heatmap_template_questions['layout'][code]
        questions = goal_survey['questions']
        answers = {}

        for q in questions:
            q_code = q['code']
            q.update(all_questions[q_code])
            answers[q_code] = json_all_answers.get(q_code)

        res[goal.code] = {
            'text': utils.be_heading_text.get(goal.code, ''),
            'questions': questions,
            'answers': answers,
            'risk': goal.risk,
            'title': goal_survey['title'],
            'code': code,
            'nav_title': surveys.be_text_lookup['break_evens'][code]['short_name'],
            'id': goal.id,
            'saved': goal.saved,
            'sdgs': utils.get_be_sdg_links(code),
        }
    return jsonify(res)



@app.route('/be/<goal_code>', methods=['POST'])
@jwt_required
def save_be_answer(goal_code):
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    answers_json = request.json
    ids = [answers_json[key]['id'] for key in answers_json]
    answers = m.BreakEvenAssessmentAnswer.query.filter(m.BreakEvenAssessmentAnswer.id.in_(ids)).all()

    for answer in answers:
        answer.value = answers_json[answer.code]['value']

    #  then re-calculate risks for goals
    bea = m.BreakEvenAssessment.query.filter_by(company_id=user.company_id).first()

    for goal in bea.goals:
        for answer in goal.answers:
            if answer.code in answers_json:
                answer.value = answers_json[answer.code]['value']

    utils.score_goals(bea)
    time.sleep(0.6)

    return 'success'
