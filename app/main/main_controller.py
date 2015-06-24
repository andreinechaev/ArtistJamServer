__author__ = 'faradey'

from flask import jsonify, request
from app.models import Event, User, News, Profile, Role
from app.main import main
from app import db
from flask.ext.login import login_required
from datetime import datetime
from sqlalchemy import exc


@main.route('/')
def hello_world():
    return 'Hello World!'


@main.route('/error')
def no_user():
    return jsonify({'message': 'error'}), 400


@main.route('/stage/all')
@login_required
def stage_all():
    if request.method == 'GET':
        events = Event.query.filter(Event.when >= datetime.today()).order_by(Event.when.asc()).all()
        events_dic = {'events': [], 'coming': [], 'new': []}
        for e in events:
            if e.when.date() == datetime.today().date():
                events_dic['events'].append({
                    'name': User.query.filter_by(id=e.user_id).first().username,
                    'title': e.name,
                    'description': e.description,
                    'lat': e.latitude,
                    'long': e.longitude,
                    'image_link': e.image_link,
                    'when': e.when.strftime("%B %d, %Y"),
                    'posted': e.posted
                })
            elif e.when.date() > datetime.today().date():
                events_dic['coming'].append({
                    'name': User.query.filter_by(id=e.user_id).first().username,
                    'title': e.name,
                    'description': e.description,
                    'lat': e.latitude,
                    'long': e.longitude,
                    'image_link': e.image_link,
                    'when': e.when.strftime("%B %d, %Y"),
                    'posted': e.posted
                })

        return jsonify(events_dic)

    return jsonify({'message': 'error'}), 404


@main.route('/stage/event/new', methods=['POST'])
@login_required
def new_event():
    json = request.json
    user_id = User.query.filter_by(username=json['username']).first().id
    name = json['title']
    image_link = json['image']
    description = json['description']
    lat = json['lat']
    lon = json['lon']
    when = json['when']
    time = datetime.strptime(when, '%d-%m-%Y %H:%M')
    if user_id is not None and name is not None and description is not None and image_link is not None:
        e = Event(user_id=user_id, name=name,
                  image_link=image_link,
                  description=description,
                  latitude=lat, longitude=lon,
                  when=time)
        try:
            db.session.add(e)
            db.session.flush()
            return jsonify({'message': 'success'})
        except exc.IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Event with the same title already exist'})
    else:
        return jsonify({'message': 'error'})


@main.route('/event/search', methods=['POST'])
@login_required
def search_event():
    json = request.json
    events = Event.query.filter(Event.when >= datetime.today()).order_by(Event.when.asc()).all()
    events_dic = {'events': []}
    for event in events:
        username = User.query.filter_by(id=event.user_id).first().username
        if json['search'].lower() not in event.name.lower() and json['search'].lower() not in username.lower():
            continue

        events_dic['events'].append({
            'name': username,
            'title': event.name,
            'description': event.description,
            'lat': event.latitude,
            'long': event.longitude,
            'image_link': event.image_link,
            'when': event.when.strftime("%B %d, %Y"),
            'posted': event.posted
        })
    return jsonify(events_dic)

@main.route('/feed/news/new', methods=['POST'])
@login_required
def new_news():
    json = request.json
    user_id = User.query.filter_by(username=json['username']).first().id
    name = json['title']
    image_link = json['image']
    description = json['description']
    if user_id is not None and name is not None and description is not None and image_link is not None:
        n = News(user_id=user_id, name=name,
                 image_link=image_link,
                 description=description)
        try:
            db.session.add(n)
            db.session.flush()
            return jsonify({'message': 'success'})
        except exc.IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'News with the same title already exist'})
    else:
        return jsonify({'message': 'error'})


@main.route('/feed/news/all', methods=['GET'])
def news_all():
    if request.method == 'GET':
        news = News.query.order_by(News.posted.desc()).all()
        news_dic = {'news': []}

        for n in news:
            news_dic['news'].append({
                'name': User.query.filter_by(id=n.user_id).first().username,
                'title': n.name,
                'description': n.description,
                'image_link': n.image_link,
                'posted': n.posted
            })

        return jsonify(news_dic)

    return jsonify({'message': 'error'}), 404


@main.route('/news/search', methods=['POST'])
@login_required
def search_news():
    json = request.json
    news = News.query.order_by(News.posted.desc()).all()
    news_dic = {'news': []}
    for n in news:
        if json['search'].lower() not in n.name.lower():
            continue
        news_dic['news'].append({
            'name': n.name,
            'image_link': n.image_link
        })
    return jsonify(news_dic)


@main.route('/users/all')
@login_required
def artist_all():
    role = Role.query.filter_by(name='artist').first()
    artists = User.query.filter_by(role_id=role.id).all()
    artist_dic = {'artists': []}
    for artist in artists:
        profile = Profile.query.filter_by(user_id=artist.id).first()
        if profile is None:
            continue
        artist_dic['artists'].append({
            'name': artist.username,
            'image_link': profile.image_link
        })
    return jsonify(artist_dic)


@main.route('/users/search', methods=['POST'])
@login_required
def search():
    json = request.json
    role = Role.query.filter_by(name='artist').first()
    artists = User.query.filter_by(role_id=role.id).all()
    artist_dic = {'artists': []}
    for artist in artists:
        # profile = Profile.query.filter_by(user_id=artist.id).first()
        if json['search'].lower() not in artist.username.lower():
            continue
        artist_dic['artists'].append({
            'name': artist.username
            # 'image_link': profile.image_link
        })
    return jsonify(artist_dic)


@main.route('/users/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        profile = Profile.query.filter_by(user_id=user.id).first()
        user_dic = {'full_name': profile.full_name,
                    'avatar': profile.image_link,
                    'about': profile.about,
                    'show_full_name': profile.show_full_name
                    }
        return jsonify(user_dic)

    return jsonify({'error': 'User does not exist'})


@main.route('/users/add_profile', methods=['POST'])
@login_required
def add_profile():
    json = request.json
    user = User.query.filter_by(username=json['username']).first()
    if user is not None:
        profile = Profile(user_id=user.id,
                          full_name=json['full_name'],
                          image_link=json['avatar'],
                          about=json['about'],
                          show_full_name=json['show_full_name'])
        try:
            db.session.add(profile)
            db.session.flush()
        except exc.IntegrityError:
            db.session.rollback()
            update_avatar(user, json['avatar'])
        return jsonify({'message': 'success'})
    return jsonify({'message': 'User does not exist'})


@main.route('/map/locations', methods=['POST'])
def map_locations():
    latitude = request.json['lat']
    longitude = request.json['lon']

    events_dic = {'events': []}
    events = Event.query.filter(Event.when >= datetime.today()).order_by(Event.posted.desc()).all()
    events = filter(
        lambda x: (latitude - 2) < x.latitude < (latitude + 2) and (longitude - 2) < x.longitude < (longitude + 2),
        events)
    for e in events:
        events_dic['events'].append({
            'author': User.query.filter_by(id=e.user_id).first().username,
            'name': e.name,
            'description': e.description,
            'lat': e.latitude,
            'long': e.longitude,
            'image_link': e.image_link,
            'when': e.when.strftime("%B %d, %Y"),
            'posted': e.posted
        })
    return jsonify(events_dic)


def update_avatar(user, image_link):
    user.image_link = image_link
    db.session.flush()
