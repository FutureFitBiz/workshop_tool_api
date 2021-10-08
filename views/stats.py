from flask import jsonify

from app import app
from lib.impact import surveys
import utils as utils
import models as m

# view isn't used atm

@app.route('/stats/be', methods=['GET'])
# @jwt_required
def get_be_stats():

    user = m.User.query.filter_by(email='tester@futurefitbusiness.org').first()
    # user = User.query.filter_by(email=get_jwt_identity()).first()
    bea = m.BreakEvenAssessment.query.filter_by(company_id=user.company.id).first()
    # res = {
    #     'break_evens': []
    # }
    data = []
    for goal in bea.goals:

        sdgs = utils.sdg_links[goal.code]

        data.append({
            'code': goal.code,
            'risk': goal.risk,
            'sdgs': str(sdgs)[1:-1],
            'stats': goal_answer_stats(goal)
        })

    return jsonify(data)


def goal_answer_stats(goal):
    stats = {}
    changes = False
    for answer in goal.answers:
        risk = answer.risk
        if not risk:
            changes = True
            # print(risk)
            risk = surveys.break_even_assessment['questions'][answer.code]['risk']
            answer.risk = risk

        if risk in stats:
            stats[risk] += 1
        else:
            stats[risk] = 1
    if changes:
        db.session.commit()
    return stats
