__author__ = 'faradey'

from flask import jsonify, request
from app.models import Event, User, News
from app.main import main
from app import db
from flask.ext.login import login_required
from datetime import datetime


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
        events = Event.query.filter(Event.when >= datetime.today()).order_by(Event.posted.desc()).all()
        events_dic = {'events': [], 'coming': []}
        for e in events:
            if e.when.date() == datetime.today().date():
                events_dic['events'].append({
                    'author': User.query.filter_by(id=e.user_id).first().username,
                    'name': e.name,
                    'description': e.description,
                    'lat': e.latitude,
                    'long': e.longitude,
                    'image_link': e.image_link,
                    'when': e.when,
                    'posted': e.posted
                })
            elif e.when.date() > datetime.today().date():
                events_dic['coming'].append({
                    'author': User.query.filter_by(id=e.user_id).first().username,
                    'name': e.name,
                    'description': e.description,
                    'lat': e.latitude,
                    'long': e.longitude,
                    'image_link': e.image_link,
                    'when': e.when,
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
        db.session.add(e)
        return jsonify({'message': 'success'})
    else:
        return jsonify({'message': 'error'})


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
        db.session.add(n)
        return jsonify({'message': 'success'})
    else:
        return jsonify({'message': 'error'})


@main.route('/feed/news/all', methods=['GET', 'POST'])
@login_required
def news_all():
    if request.method == 'GET':
        news = News.query.order_by(News.posted.desc()).all()
        news_dic = {'news': []}

        for n in news:
            news_dic['news'].append({
                'author': User.query.filter_by(id=n.user_id).first().username,
                'name': n.name,
                'description': n.description,
                'image_link': n.image_link,
                'posted': n.posted
            })

        return jsonify(news_dic)

    return jsonify({'message': 'error'}), 404


