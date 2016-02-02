from flask.ext.login import logout_user, login_required, login_user
from flask import request, jsonify
from validate_email import validate_email
from app.authentication import auth
from app.models import User, Role
from app import db


@auth.route('/auth/signup', methods=['POST'])
def sign_up():
    username = request.args.get("username")
    password = request.args.get("password")
    email = request.args.get("email")
    role_name = request.args.get("role")

    # json_req = request.json
    # username = json_req['username']
    # email = json_req['email']
    # password = json_req['password']
    # role_name = json_req['role']
    if exist_with_name(username):
        return jsonify({'message': 'User with this name already exist'}), 400
    if exist_with_email(email):
        return jsonify({'message': 'User with this email already exist'}), 400
    if check_user(username, password, email, role_name):
        return jsonify({'message': 'Incorrect data, check all fields'}), 400
    else:
        role = Role.query.filter_by(name=role_name).first()
        user = User(email=email, username=username, password=password, role=role)
        db.session.add(user)
        return jsonify({'message': 'success'})


@auth.route('/auth/signin', methods=['POST'])
def sign_in():
    username = request.args.get("username")
    password = request.args.get("password")
    # json_req = request.json
    # user = User.query.filter_by(username=json_req['username']).first()
    user = User.query.filter_by(username=username).first()
    if user is not None and user.verify_password(password):
        login_user(user)
        return jsonify({'message': 'success',
                        'role': user.role.name,
                        'has_profile': user.has_profile()})

    return jsonify({'message': 'Incorrect username/password'}), 400


@auth.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'success'})


def check_user(username, password, email, role_name):
    is_valid = validate_email(email)
    if not is_valid or len(password) < 6 or len(username) < 4 or not (role_name == 'fan' or role_name == 'artist'):
        return True
    else:
        return False


def exist_with_name(username):
    if User.query.filter_by(username=username).first() is not None:
        return True
    else:
        return False


def exist_with_email(email):
    if User.query.filter_by(email=email).first() is not None:
        return True
    else:
        return False
