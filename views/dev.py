import json
import os

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app, db, bcrypt
import utils as utils
import models as m
import config.settings as settings



#
# dev views
# trying to remember to comment them when not in use
# as don't want half of these to be active in production ahah
#

# @app.route('/xoxo', methods=['GET'])
# def set_xoxo():
#     impacts = Impact.query.filter_by(property_code='').all()
#     count = len(impacts)
#     for i in impacts:
#         i.property_code = 'X-0'
#
#     db.session.commit()
#     return jsonify({'blank to X-0': count})

# @app.route('/meh', methods=['GET'])
# def set_everyones_stuff_to_false():
#     """
#     added 'mark impact as n/a'
#     so default all current impacts to true,
#     """
#     impacts = Impact.query.all()
#     for i in impacts:
#         i.active = True
#
#     db.session.commit()
#     return jsonify({'status': 'oh ja'})


@app.route('/reset/test', methods=['GET'])
def whatisgoingon():
    """
    reset the tester@ password
    used for testing the reset password email
    """
    user = m.User.query.filter_by(email='tester@futurefitbusiness.org').first()
    print(user)
    user.password = utils.new_bcrypt_password('123456')
    db.session.commit()
    return jsonify({'status': 'success'})

# @app.route('/reset/lll', methods=['GET'])
# def whatisgoingonaha():
#     """
#     reset everyones passwords for localhost, so we can play with test data from staging
#     """
#     user = User.query.all()
#     for u in user:
#         u.password = utils.new_bcrypt_password('123456')
#     db.session.commit()
#     return jsonify({'status': 'success'})

# @app.route('/what', methods=['GET'])
# def reset_test():
#     return jsonify({
#         'status': settings.DATABASE_URI,
#         'mode': os.environ.get('APP_MODE'),
#         })


# @app.route('/delete_company', methods=['GET'])
# @jwt_required
# def test_delete_company():
#     """
#     ACTUALLY delete a company, not sure we use this yet?
#     """
#     email = get_jwt_identity()
#     company = Company.query.\
#         join(User).\
#         filter(User.email == email).first()
#     db.session.delete(company)
#     db.session.commit()
#     return jsonify({'status': 'success'})


# @app.route('/delete_products', methods=['GET'])
# @jwt_required
# def test_delete_products():
#     # this is just a test url
#     email = get_jwt_identity()
#     s = Product.query.all()
#     for sur in s:
#         db.session.delete(sur)
#
#     db.session.commit()
#     return jsonify({'status': 'success'})


@app.route('/db_setup', methods=['GET'])
# @jwt_required
def get_db_setup():
    """
    first time db setup
    to add all our users mainly/etc
    """
    res = {}

    # # add a non admin
    # email = 'basicuser@ff.com'
    # non_admin_test = m.User.query.filter_by(email=email).first()
    # if not non_admin_test:
    #     user = m.User()
    #     user.password = bcrypt.generate_password_hash('123456').decode('utf - 8')
    #     user.email = email
    #     user.first = 'basic'
    #     user.admin = False
    #     db.session.add(user)
    #     db.session.commit()
    #     res[email] = 'ok'
    # else:
    #     res[email] = 'user exists'

    # add ff users
    users = [
        'tester',
        'yasmin',
        'geoff',
        'kevin',
        'stephanie',
        'anna',
        'astrid',
        'tom',
        'martin',
    ]
    for u in users:
        try:
            email = u + '@futurefitbusiness.org'
            check = m.User.query.filter_by(email=email).first()
            if not check:
                user = m.User()
                user.password = bcrypt.generate_password_hash('123456').decode('utf - 8')
                user.email = email
                user.first = u
                user.admin = True
                user.investor = True
                db.session.add(user)
                db.session.commit()
                res[email] = 'ok'
            else:
                res[email] = 'user exists'
        except Exception as e:
            res[email] = str(e)

    return jsonify(res)



#
# @app.route('/ff')
# def all_combinations_of_properties():
#     """
#     i got lost,
#     this is unfinished
#
#     I was trying to get all combinations of options ticked
#     """
#     # get all faet codes
#     all_facets = []
#     for q in surveys.facets['questions']:
#         o = q.get('options')
#         if o:
#             all_facets += get_all_answer_codes(o)
#
#     #  get all property codes
#     all_property_codes = []
#     for q in surveys.properties['questions']:
#         id = q['logic']
#         if id:
#             all_property_codes.append(id[0][0])
#
#     all_property_codes = sorted(list(set(all_property_codes)))
#
#     # all property answers:
#     all_answers = []
#     for q in surveys.properties['questions']:
#         o = q.get('options')
#         if o:
#             all_answers += get_all_answer_codes(o)
#
#     # print(all_answers)
#
#     impacts = []
#     for a in all_property_codes:
#         code = a[0] + a[-1]
#         property_answers = [x for x in all_answers if code in x]
#         # print('===============')
#         # print(property_answers)
#         impacts += get_property_actions(property_answers, a, all_facets)
#
#     impacts = merge_duplicate_impacts_as_list(impacts)
#
#     # impacts = sorted(impacts, key=attrgetter('option_code'))
#     print(len(impacts))
#
#     with open('./descriptions_for_kev.csv', 'w', newline='') as csvfile:
#         spamwriter = csv.writer(csvfile, delimiter=',')
#         spamwriter.writerow(['pp action', 'option text', 'option code', 'property code', 'sdgs'])
#         for i in impacts:
#             spamwriter.writerow([
#                 i['pp'],
#                 i['option_text'],
#                 i['option_code'],
#                 i['property_code'],
#                 i['sdgs'],
#
#             ])
#
#     return jsonify(impacts)
