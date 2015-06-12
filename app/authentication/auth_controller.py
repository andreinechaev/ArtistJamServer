__author__ = 'faradey'

from flask.ext.login import logout_user, login_required, login_user

from flask import request, jsonify
from validate_email import validate_email
from app.authentication import auth
from app.models import User, Role
from app import db


@auth.route('/signup', methods=['POST'])
def sign_up():
    json_req = request.json
    username = json_req['username']
    email = json_req['email']
    password = json_req['password']
    role_name = json_req['role']
    is_valid = validate_email(email)
    print '%s %s %s %s' % (username, email, password, role_name)
    if not is_valid or len(password) < 6 or len(username) < 4 and (role_name == 'fun' or role_name == 'artist'):
        return jsonify({'message': 'error'}), 404

    role = Role.query.filter_by(name=role_name).first()
    user = User(email=email, username=username, password=password, role=role)
    db.session.add(user)
    return jsonify({'message': 'success'})


@auth.route('/signin', methods=['POST'])
def sign_in():
    json_req = request.json
    user = User.query.filter_by(username=json_req['username']).first()

    if user is not None and user.verify_password(json_req['password']):
        login_user(user)
        role = Role.query.filter_by(id=user.role_id).first()
        print role, user.role_id
        return jsonify({'message': 'success',
                        'role': role.name})

    return jsonify({'message': 'error'}), 404


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'success'})
