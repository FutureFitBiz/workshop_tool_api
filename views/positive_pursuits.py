import time

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app, settings, db
from lib.impact import surveys, get_hidden_options, get_property_actions,\
    merge_duplicate_impacts, assign_automatic_impacts,\
    get_impact_description, get_impact_description_from_dict, get_impact_percent_complete_stats,\
    get_impact_question_lookup

import utils as utils
import models as m


@app.route('/pp/sankey', methods=['GET'])
@jwt_required
def get_a_positive_sankey():
    # user = m.User.query.filter_by(email='tester@futurefitbusiness.org').first()
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    all_nodes = []
    product_nodes = []
    sdg_nodes = []
    links = []
    # print(surveys.be_text_lookup)

    for product in user.company.products:
        product_nodes.append(product.name)

        for impact in product.impacts:
            sdgs = [x.sdg.split('.')[0] for x in impact.sdgs if x.sdg != '']
            sdgs = list(set(sdgs))
            if impact.active:
                for sdg in sdgs:
                    # sdg_main = sdg.split('.')[0]
                    action = impact.pp_action.split('.')[0]
                    action_text = surveys.pp_text_lookup[action]
                    sdg_nodes.append(sdg)
                    links.append({
                        'source': product.name,
                        'product_name': product.name,
                        'target': sdg,
                        'sdg': sdg,
                        'sdg_text': utils.sdgs[sdg]['title'],
                        # 'sdg': sdg_main,
                        'value': 1,
                        # 'sdg_target': sdg,
                        'pp': action,
                        'pp_text': action_text,
                        'text': impact.option_text
                    })

    product_nodes = list(set(product_nodes))
    sdg_nodes = list(set(sdg_nodes))
    product_nodes.sort()
    sdg_nodes.sort(key=lambda x: int(x))

    all_nodes = product_nodes + sdg_nodes

    nodes = []
    id = 0
    lookup = {}
    for node in all_nodes:
        nodes.append({'name': node})
        lookup[node] = id
        id += 1

    for link in links:
        source = link['source']
        link['source'] = lookup[source]
        target = link['target']
        link['target'] = lookup[target]

    return jsonify({
        'nodes': nodes,
        'links': links
    })


@app.route('/pp', methods=['GET'])
@jwt_required
def get_all_pp():
    res = {}
    user = m.User.query.filter_by(email=get_jwt_identity()).first()

    for product in user.company.products:
        impacts = []
        current_impacts = m.Impact.query.filter_by(product_id=product.id).all()
        product_sdgs = []
        for i, impact in enumerate(current_impacts, 1):
            sdgs = [x.sdg for x in impact.sdgs if x.sdg != '']
            sdgs = sorted(sdgs, key=lambda x: utils.sdg_key(x))
            product_sdgs += sdgs
            sdgs = ', '.join(sdgs)

            impacts.append({
                'number': i,
                'id': impact.id,
                'pp': impact.pp_action,
                'description': get_impact_description(impact),
                'sdgs': sdgs,
            })

        sdg_targets = []

        if product_sdgs:
            sdgs = []
            for sdg_target in product_sdgs:
                sdg = sdg_target.split('.')[0]
                if sdg not in sdgs:
                    sdgs.append(sdg)
                if sdg_target not in sdg_targets:
                    sdg_targets.append(sdg_target)

            product_sdgs = sorted(sdgs, reverse=True)
            product_sdgs = ', '.join(product_sdgs)
            sdg_targets = sorted(sdg_targets, reverse=True)
            sdg_targets = ', '.join(sdg_targets)
        else:
            product_sdgs = ''
            sdg_targets = ''

        res[product.code] = {
            'id': product.id,
            'name': product.name.capitalize(),
            'code': product.code,
            'setup_complete': product.setup_complete,
            'impacts': impacts,
            'sdgs': product_sdgs,
            'sdg_targets': sdg_targets,
        }

    return jsonify(res)



@app.route('/product', methods=['POST'])
@jwt_required
def add_new_product():
    data = request.json.get('data')
    user = m.User.query.filter_by(email=get_jwt_identity()).first()

    product = m.Product()
    product.company_id = user.company.id
    product.code = utils.random_uuid_code(13)
    product.name = data['AE-1']
    product.description = data.get('AE-2')
    product.revenue_type = data.get('AE-3')
    product.revenue = data.get('AE-4')
    product.cost = data.get('AE-5')
    product.stage = data.get('AE-6')
    product.known_costs = data.get('AE-7')
    db.session.add(product)

    db.session.commit()

    return jsonify({
        'status': 'success',
    })


@app.route('/product/<int:id>', methods=['POST'])
@jwt_required
def update_product(id):
    data = request.json.get('data')
    product = m.Product.query.get(id)
    product.name = data['AE-1']
    product.description = data.get('AE-2')
    product.revenue_type = data.get('AE-3')
    product.revenue = data.get('AE-4')
    product.cost = data.get('AE-5')
    product.stage = data.get('AE-6')
    product.known_costs = data.get('AE-7')
    db.session.commit()

    return jsonify({'status': 'success', })


@app.route('/product/edit/<int:id>', methods=['GET'])
@jwt_required
def get_edit_product(id):
    product = m.Product.query.get(id)
    answers = {
        # because of how it parses csv
        # and until we have a better way..
        'AE-1': product.name,
        'AE-2': product.description,
        'AE-3': product.revenue_type,
        'AE-4': product.revenue,
        'AE-5': product.cost,
        'AE-6': product.stage,
        'AE-7': product.known_costs,
    }
    return jsonify(answers)


@app.route('/product/delete/<int:id>', methods=['GET'])
# @jwt_required
def delete_products(id):
    response = {'status': 'success'}
    product = m.Product.query.get(id)

    if product:
        db.session.delete(product)
        db.session.commit()
    else:
        response = {
            'status': 'error',
            'message': 'no product to delete'
        }

    return jsonify(response)


@app.route('/pp/activity_questions/part1', methods=['GET'])
# @jwt_required
def get_facet_questions():
    questions = surveys.facets['questions'][2:-1]
    return jsonify(questions)


@app.route('/pp/activity_questions/part2', methods=['POST'])
# @jwt_required
def get_setup_part_2_questions():
    facets = request.get_json()
    survey = {}
    hidden_options = []
    questions = surveys.properties['questions'][2:]

    for question in questions:
        if question['type'] == 'checkbox':
            hidden_options += get_hidden_options(question['options'], facets)

    return jsonify({
        'questions': questions,
        'hidden_options': hidden_options
    })


@app.route('/pp/activity/new', methods=['POST'])
@jwt_required
def save_setup():
    user = m.User.query.filter_by(email=get_jwt_identity()).first()
    data = request.get_json()
    p = m.Product()
    p.company_id = user.company.id
    p.name = data['name']
    p.code = utils.random_uuid_code(13)
    db.session.add(p)
    db.session.commit()

    add_part_1(p.id, data['part_1_answers'])
    add_part_2(p.id, data['part_1_answers'], data['part_2_answers'])
    db.session.commit()

    return jsonify({
        'name': p.name,
        'code': p.code,
        'id': p.id,
    })


def add_part_1(product_id, part_1_answers):
    for code in part_1_answers:
        add = m.ProductFacet()
        add.product_id = product_id
        add.code = code
        db.session.add(add)


def add_part_2(product_id, part_1_answers, part_2_answers):
    updated_properties = {}
    # group them per X
    for code in part_2_answers:
        token = code.split('-')[0]
        if token not in updated_properties:
            updated_properties[token] = []

        updated_properties[token].append(code)

    for property in updated_properties.keys():
        pp = m.ProductProperty()
        pp.product_id = product_id
        pp.code = property
        db.session.add(pp)
        for answer in updated_properties[property]:
            sa = m.ProductPropertyAnswer()
            sa.code = answer
            pp.answers.append(sa)

    # great we have done this all, lets calculate the actions if it is the second setup
    calculate_impacts(part_1_answers, updated_properties, product_id)


def get_parent_property(code):
    res = code
    dots = code.count('.')
    if dots > 1:
        res = code.split('.')[0]
    return res


def calculate_impacts(facet_codes, properties, product_id):
    # Go through the answered surveys for the product and get the recommended actions
    # get current selected facets
    changes = {}
    impacts = []

    # property = X1, X2, etc
    for property_code in properties.keys():
        answers = sorted(properties[property_code])
        property_code = "X-1.{}".format(property_code[1])
        impacts += get_property_actions(answers, property_code, facet_codes)

    impacts = assign_automatic_impacts(impacts, facet_codes)
    impacts = merge_duplicate_impacts(impacts)

    # TODO: uhh be more efficent at deleting, only remove what has changed...
    # this is fastest for now!
    current_impacts = m.Impact.query.filter_by(product_id=product_id).all()
    existing_impacts = []

    for ci in current_impacts:
        key = ci.option_text + ci.pp_action
        existing_impacts.append(key)

        impact_info = {
            'property_code': ci.property_code,
            'option_text': ci.option_text,
            'pp': ci.pp_action
        }

        property = get_parent_property(ci.property_code)

        if property not in changes:
            # if there's no code.. its probably an 'automatic', ie x-0 impact - or its broke af lololol
            name = surveys.property_title_lookup[ci.property_code]

            changes[property] = {
                'deleted': [],
                'added': [],
                'modified': [],
                'name': name
            }

        if key not in impacts:
            changes[property]['deleted'].append({
                'code': ci.property_code,
                'text': ci.option_text,
                'sdgs': ', '.join([x.sdg for x in ci.sdgs])
            })

            db.session.delete(ci)
        else:
            modified = False
            updated_impact = impacts[key]
            existing_sdgs = []
            for sdg in ci.sdgs:
                if sdg.sdg not in updated_impact['sdgs']:
                    modified = True
                    db.session.delete(sdg)
                else:
                    existing_sdgs.append(sdg.sdg)

            for sdg in updated_impact['sdgs']:
                if sdg not in existing_sdgs:
                    modified = True
                    sdg_add = m.ImpactSdg()
                    sdg_add.sdg = sdg
                    db.session.add(sdg_add)
                    ci.sdgs.append(sdg_add)

            if modified:
                changes[property]['modified'].append({
                    'sdgs': ','.join(updated_impact['sdgs']),
                    'code': updated_impact['property_code'],
                    'text': updated_impact['option_text']
                })

    for key in impacts:
        if key not in existing_impacts:
            impact = impacts[key]
            add = m.Impact()
            add.property_code = impact['property_code']
            add.option_text = impact['option_text']
            add.option_code = impact['option_code']
            add.pp_action = impact['pp']
            add.product_id = product_id
            db.session.add(add)

            for sdg in impact['sdgs']:
                if sdg:
                    # get rid of blank ones
                    sdg_add = m.ImpactSdg()
                    sdg_add.sdg = sdg
                    db.session.add(sdg_add)
                    add.sdgs.append(sdg_add)

            property = get_parent_property(impact['property_code'])

            if property not in changes:
                changes[property] = {
                    'deleted': [],
                    'added': [],
                    'modified': [],
                    'name': surveys.property_description_lookup[property]
                }

            changes[property]['added'].append({
                'sdgs': ', '.join(impact['sdgs']),
                'code': impact['property_code'],
                'pp': impact['pp'],
                'text': get_impact_description_from_dict(impact)
            })

    return changes


@app.route('/product/<int:product_id>/property/stats', methods=['POST'])
@jwt_required
def get_property_stats(product_id):
    data = request.json.get('data')

    current_properties = m.ProductProperty.query.filter_by(product_id=product_id).all()
    for property in current_properties:
        for answer in property.answers:
            pass

    return jsonify({'status': 'success'})


@app.route('/product/<int:product_id>/impacts', methods=['GET'])
@jwt_required
def get_product_impacts(product_id):
    impacts = []
    question_lookup = get_impact_question_lookup()

    current_impacts = m.Impact.query.filter_by(product_id=product_id).all()

    for i, current_impact in enumerate(current_impacts, 1):
        # # TODO: go through and add the full option list
        # ie, "Energy > Some option > Some suboption that you clicked"
        sdgs = [x.sdg for x in current_impact.sdgs if x.sdg != '']
        sdgs = sorted(sdgs, key=lambda x: utils.sdg_key(x))
        sdgs = ', '.join(sdgs)

        completed_stats = get_impact_percent_complete_stats(question_lookup, current_impact.id)

        impacts.append({
            'number': i,
            'id': current_impact.id,
            'pp': current_impact.pp_action,
            'property_code': current_impact.property_code,
            'option': current_impact.option_code,
            'text': current_impact.option_text,
            'active': current_impact.active,
            'completed': completed_stats['percent_complete'] == 100,
            'description': get_impact_description(current_impact),
            'pp_text': surveys.pp_text_lookup[current_impact.pp_action],
            'sdgs': sdgs,
            'visible_questions': completed_stats['visible_questions'],
            'percent_complete': completed_stats['percent_complete'],
            'answered_questions': completed_stats['answered_questions']
        })

    return jsonify(impacts)


@app.route('/product/<int:product_id>/impact/<int:impact_id>', methods=['GET'])
@jwt_required
def get_impact_data(product_id, impact_id):
    # get the current answers for the action_id - what the name says!
    answers = {}
    external_answers = {}

    current_answers = m.ImpactAnswer.query.filter_by(impact_id=impact_id).all()
    for answer in current_answers:
        answers[answer.number] = answer.text if answer.text else answer.data

    return jsonify({
        'answers': answers,
    })


@app.route('/product/<int:product_id>/impact/<int:impact_id>', methods=['POST'])
@jwt_required
def save_impact_data(product_id, impact_id):
    data = request.json.get('data')

    # clean out old - we should be more clever about this, ie only update ones that have changed
    # rather then delete and re-add, however this is wayyyy cleaner and faster to code for now until
    # we are happy and have tested this stuffs
    current_answers = m.ImpactAnswer.query.filter_by(impact_id=impact_id).all()
    for current_answer in current_answers:
        db.session.delete(current_answer)

    for key in data['answers'].keys():
        # only add if there is actual data
        if len(data['answers'][key]) > 0:
            add = m.ImpactAnswer()
            add.impact_id = impact_id
            add.number = key
            # check the question type
            type = get_impact_question_type(key)
            if type == 'text area':
                add.text = data['answers'][key]
                pass
            else:
                add.data = data['answers'][key]

            db.session.add(add)

    db.session.commit()

    return jsonify({
        'success': True,
    })


def get_impact_question_type(key):
    for question in surveys.pp_action['questions']:
        value = question.get('value')
        if value and value == key:
            return question.get('type')


@app.route('/product/impact/<int:impact_id>/set_active/<active>', methods=['POST'])
@jwt_required
def toggle_impact_active(impact_id, active):
    # Qustion for Raph - do we need to always pass the product id for impact editing? i don't think we should have to?
    impact = m.Impact.query.filter_by(id=impact_id).one()
    impact.active = (active == 'true')
    db.session.commit()

    return jsonify({
        'success': True,
    })
