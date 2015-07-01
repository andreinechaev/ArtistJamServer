__author__ = 'faradey'

from flask import jsonify, request
from app.models import User, Profile, Role
from app.main import main
from app import db, cache
from flask.ext.login import login_required, current_user
from sqlalchemy import exc, func


@main.route('/users/all')
@login_required
@cache.cached(timeout=1)
def artist_all():
    role = Role.query.filter_by(name='artist').first()
    artists = User.query.filter_by(role_id=role.id).all()
    artist_dic = {'artists': []}
    for artist in artists:
        try:
            artist.profile.id
        except Exception:
            continue
        artist_dic['artists'].append({
            'username': artist.username,
            'following': current_user.is_following(artist),
            'followers': artist.followers.count(),
            'avatar': artist.profile.image_link,
            'description': artist.profile.about
        })
    return jsonify(artist_dic)


@main.route('/users/search', methods=['POST'])
@login_required
@cache.cached(timeout=1)
def search():
    # print current_user.role.name
    json = request.json
    # role = Role.query.filter_by(name='artist').first()
    artists = User.query.filter(User.role_id == 2).filter(
        func.lower(User.username).contains(json['search'].lower())).all()
    artist_dic = {'artists': []}
    for artist in artists:
        print artist.has_profile()
        artist_dic['artists'].append({
            'username': artist.username,
            'following': current_user.is_following(artist),
            'avatar': artist.profile.image_link,
            'description': artist.profile.about
        })
    return jsonify(artist_dic)


@main.route('/users/<username>')
@login_required
@cache.cached(timeout=1)
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        profile = Profile.query.filter_by(user_id=user.id).first()
        user_dic = {
            'full_name': profile.full_name,
            'avatar': profile.image_link,
            'about': profile.about,
            'followers': user.followers.count(),
            'show_full_name': profile.show_full_name
        }
        return jsonify(user_dic)

    return jsonify({'error': 'User does not exist'})


@main.route('/users/add_profile', methods=['POST'])
@login_required
def add_profile():
    json = request.json
    user = current_user
    if user is not None:
        try:
            user.profile = Profile(user_id=user.id,
                                   full_name=json['full_name'],
                                   image_link=json['avatar'],
                                   about=json['about'],
                                   show_full_name=json['show_full_name'])
            db.session.flush()
        except exc.IntegrityError:
            db.session.rollback()
            update_avatar(json)

        return jsonify({'message': 'success'})
    return jsonify({'message': 'User does not exist'})


def update_avatar(json):
    current_user.profile.image_link = json['avatar']
    current_user.profile.about = json['about']
    db.session.flush()


@main.route('/users/follow/<username>')
@login_required
def follow(username):
    print username
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'error': 'Invalid user'})
    if user == current_user:
        return jsonify({'error': 'You cannot follow yourself'})
    if current_user.is_following(user):
        return jsonify({'error': 'Already following'})
    current_user.follow(user)
    return jsonify({'message': 'Success'})


@main.route('/users/unfollow/<username>')
@login_required
def unfillow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'error': 'Invalid user'})
    if not current_user.is_following(user):
        return jsonify({'error': 'You are not following that user'})
    current_user.unfollow(user)
    return jsonify({'message': 'Success'})


@main.route('/users/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'Success'})
    return jsonify({'message': user.followers.count()})
