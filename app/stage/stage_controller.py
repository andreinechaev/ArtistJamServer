__author__ = 'faradey'

from datetime import datetime, timedelta

from app.stage import stage
from flask import jsonify
from app.models import Event
from app import cache
from flask.ext.login import login_required


@stage.route('/stage/today')
@login_required
@cache.cached(timeout=5)
def stage_today():
    events = Event.query.filter((datetime.today() - timedelta(hours=12)) <= Event.when).filter(
        (datetime.today() + timedelta(hours=12)) > Event.when).order_by(
        Event.when.asc()).all()

    events_dic = {'today': []}
    for e in events:
        username = e.user.username
        time_of_event = e.when.strftime("%m %d, %Y %H:%M")
        if e.when.date() == datetime.today().date():
            events_dic['today'].append({
                'id': e.id,
                'username': username,
                'title': e.name,
                'description': e.description,
                'lat': e.latitude,
                'long': e.longitude,
                'image_link': e.image_link,
                'when': time_of_event
            })

    return jsonify(events_dic)


@stage.route('/stage/coming')
@login_required
@cache.cached(timeout=5)
def stage_coming():
    events = Event.query.filter(Event.when > datetime.today()).order_by(
        Event.when.asc()).all()
    events_dic = {'coming': []}
    for e in events:
        username = e.user.username
        time_of_event = e.when.strftime("%m %d, %Y %H:%M")
        events_dic['coming'].append({
            'id': e.id,
            'username': username,
            'title': e.name,
            'description': e.description,
            'lat': e.latitude,
            'long': e.longitude,
            'image_link': e.image_link,
            'when': time_of_event
        })

    return jsonify(events_dic)


@stage.route('/stage/new')
@login_required
@cache.cached(timeout=5)
def stage_new():
    events = Event.query.filter(Event.when >= datetime.today()).order_by(
        Event.when.asc()).all()
    events_dic = {'new': []}
    for e in events:
        username = e.user.username
        time_of_event = e.when.strftime("%m %d, %Y %H:%M")
        if e.user.since < (datetime.today() - timedelta(days=7)):
            events_dic['new'].append({
                'id': e.id,
                'username': username,
                'title': e.name,
                'description': e.description,
                'lat': e.latitude,
                'long': e.longitude,
                'image_link': e.image_link,
                'when': time_of_event,
            })

    return jsonify(events_dic)

