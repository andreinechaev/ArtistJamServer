from datetime import datetime, timedelta
from flask import jsonify, request, render_template
from app.models import Event, News, User
from app.main import main
from app import db, cache
from flask.ext.login import login_required, current_user
from sqlalchemy import exc, func


@main.route('/')
@cache.cached(timeout=200)
def index():
    news = News.query.order_by(News.posted.desc()).limit(10)
    return render_template('main.html', news=news)


@main.route('/error')
def no_user():
    return jsonify({'message': 'error'}), 400


@main.route('/privacy/<privacy_page>')
def privacy(privacy_page):
    return render_template(privacy_page + '.html')


@main.route('/stage/all')
@login_required
@cache.cached(timeout=5)
def stage_all():
    if request.method == 'GET':
        events = Event.query.filter(Event.when >= (datetime.today() - timedelta(hours=12))).order_by(
            Event.when.asc()).all()
        events_dic = {'today': [], 'coming': [], 'new': []}
        for e in events:
            username = e.user.username
            about = e.user.profile.about
            time_of_event = e.when.strftime("%m %d, %Y %H:%M")
            if e.when.date() == datetime.today().date():
                events_dic['today'].append({
                    'id': e.id,
                    'username': username,
                    'about': about,
                    'title': e.name,
                    'description': e.description,
                    'lat': e.latitude,
                    'long': e.longitude,
                    'image_link': e.image_link,
                    'when': time_of_event,
                })
            elif e.when.date() > datetime.today().date():
                events_dic['coming'].append({
                    'id': e.id,
                    'username': username,
                    'about': about,
                    'title': e.name,
                    'description': e.description,
                    'lat': e.latitude,
                    'long': e.longitude,
                    'image_link': e.image_link,
                    'when': time_of_event,
                })
            if e.user.since > (datetime.today() - timedelta(days=7)):
                events_dic['new'].append({
                    'id': e.id,
                    'username': username,
                    'about': about,
                    'title': e.name,
                    'description': e.description,
                    'lat': e.latitude,
                    'long': e.longitude,
                    'image_link': e.image_link,
                    'when': time_of_event,
                })
        return jsonify(events_dic)

    return jsonify({'message': 'error'}), 404


@main.route('/stage/event/new', methods=['POST'])
@login_required
def new_event():
    json = request.json
    user_id = current_user.id
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


@main.route('/event/<event_id>')
@login_required
@cache.cached(timeout=500)
def event_by_id(event_id):
    e = Event.query.filter_by(id=int(event_id)).first()
    if e is None:
        return jsonify({'error': 'Not found'}), 404

    try:
        avatar = e.user.profile.image_link
        about = e.user.profile.about
    except Exception:
        avatar = 'None'
        about = 'None'

    e_dic = {
        'id': e.id,
        'username': e.user.username,
        'about': about,
        'followers': e.user.followers.count(),
        'title': e.name,
        'avatar': avatar,
        'description': e.description,
        'lat': e.latitude,
        'long': e.longitude,
        'image_link': e.image_link,
        'when': e.when.strftime("%m %d, %Y %H:%M"),
    }
    return jsonify(e_dic)


@main.route('/events/<username>')
@login_required
@cache.cached(timeout=25)
def event_for_user(username):
    user = User.query.filter_by(username=username).first()
    event_dic = {'events': []}
    for e in user.events:
        try:
            avatar = e.user.profile.image_link
            about = e.user.profile.about
        except Exception:
            avatar = 'None'
            about = 'None'
        event_dic['events'].append({
            'id': e.id,
            'username': username,
            'about': about,
            'followers': e.user.followers.count(),
            'title': e.name,
            'avatar': avatar,
            'description': e.description,
            'lat': e.latitude,
            'long': e.longitude,
            'image_link': e.image_link,
            'when': e.when.strftime("%m %d, %Y %H:%M"),
            'posted': e.posted
        })
    return jsonify(event_dic)


@main.route('/event/search')
@login_required
def search_event():
    search = request.args.get('search')
    events = Event.query.filter(Event.when >= datetime.today())\
        .order_by(Event.when.asc())\
        .filter(func.lower(Event.name).contains(search.lower())).all()
    events_dic = {'events': []}
    for event in events:
        events_dic['events'].append({
            'username': event.user.username,
            'title': event.name,
            'description': event.description,
            'lat': event.latitude,
            'long': event.longitude,
            'image_link': event.image_link,
            'when': event.when.strftime("%B %d, %Y %H:%M"),
            'posted': event.posted
        })
    return jsonify(events_dic)


@main.route('/feed/news/new', methods=['POST'])
@login_required
def new_news():
    json = request.json
    user_id = current_user.id
    name = json['title']
    image_link = json['image']
    description = json['description']
    if user_id is not None and name is not None and description is not None and image_link is not None:
        n = News(user_id=user_id,
                 name=name,
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
        return jsonify({'message': 'error'}), 404


@main.route('/feed/news/all')
def news_all():
    news = News.query.order_by(News.posted.desc()).all()
    news_dic = {'news': []}
    for n in news:
        news_dic['news'].append({
            'id': n.id,
            'liked': current_user.is_like(n),
            'likes': n.count_likes(),
            'username': n.user.username,
            'title': n.name,
            'description': n.description,
            'image_link': n.image_link,
        })

    return jsonify(news_dic)


@main.route('/news/<username>')
@login_required
def new_for_user(username):
    user = User.query.filter_by(username=username).first()
    news_dic = {'news': []}
    for n in user.news:
        try:
            avatar = n.user.profile.image_link
            about = n.user.profile.about
        except Exception:
            avatar = 'None'
            about = 'None'
        news_dic['news'].append({
            'id': n.id,
            'liked': current_user.is_like(n),
            'likes': n.count_likes(),
            'avatar': avatar,
            'username': n.user.username,
            'about': about,
            'followers': n.user.followers.count(),
            'title': n.name,
            'description': n.description,
            'image_link': n.image_link,
            'posted': n.posted.strftime("%B %d, %Y %H:%M")
        })
    return jsonify(news_dic)


@main.route('/news/<news_id>')
@login_required
@cache.cached(timeout=500)
def news_by_id(news_id):
    n = News.query.filter_by(id=int(news_id)).first()
    if n is None:
        return 404

    try:
        avatar = n.user.profile.image_link
        about = n.user.profile.about
    except Exception:
        avatar = 'None'
        about = 'None'
    news_dic = {
        'id': n.id,
        'liked': current_user.is_like(n),
        'likes': n.count_likes(),
        'avatar': avatar,
        'username': n.user.username,
        'about': about,
        'followers': n.user.followers.count(),
        'title': n.name,
        'description': n.description,
        'image_link': n.image_link,
        'posted': n.posted.strftime("%B %d, %Y %H:%M")
    }
    return jsonify(news_dic)


@main.route('/news/search')
@login_required
def search_news():
    search = request.args.get('search')
    news = News.query.order_by(News.posted.desc()).filter(
        func.lower(News.name).contains(search.lower())).all()
    news_dic = {'news': []}
    for n in news:
        try:
            avatar = n.user.profile.image_link
            about = n.user.profile.about
        except Exception:
            avatar = 'None'
            about = 'None'
        news_dic['news'].append({
            'id': n.id,
            'liked': current_user.is_like(n),
            'likes': n.count_likes(),
            'avatar': avatar,
            'username': n.user.username,
            'about': about,
            'followers': n.user.followers.count(),
            'title': n.name,
            'description': n.description,
            'image_link': n.image_link,
            'posted': n.posted.strftime("%B %d, %Y %H:%M")
        })
    return jsonify(news_dic)


@main.route('/map/locations', methods=['POST'])
@login_required
@cache.cached(timeout=50)
def map_locations():
    latitude = request.json['lat']
    longitude = request.json['lon']
    events_dic = {'events': []}
    events = Event.query.filter(Event.when >= datetime.today()).order_by(Event.when.desc()).all()
    events = filter(
        lambda x: (latitude - 2) < x.latitude < (latitude + 2) and (longitude - 2) < x.longitude < (longitude + 2),
        events)
    for e in events:
        try:
            avatar = e.user.profile.image_link
        except Exception:
            avatar = 'None'
        events_dic['events'].append({
            'username': e.user.username,
            'about': e.user.profile.about,
            'followers': e.user.followers.count(),
            'title': e.name,
            'avatar': avatar,
            'description': e.description,
            'lat': e.latitude,
            'long': e.longitude,
            'image_link': e.image_link,
            'when': e.when.strftime("%B %d, %Y %H:%M")
        })
    return jsonify(events_dic)


@main.route('/jam')
@login_required
def jam():
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    events = Event.query.filter(Event.when >= datetime.today()).order_by(Event.when.desc()).all()
    events = filter(
        lambda x: (latitude - 0.01) < x.latitude < (latitude + 0.01) and (longitude - 0.01) < x.longitude < (
            longitude + 0.01),
        events)
    if len(events) > 0:
        e = events[0]
        try:
            avatar = e.user.profile.image_link
        except Exception:
            avatar = 'None'
        events_dic = {
            'username': e.user.username,
            'about': e.user.profile.about,
            'followers': e.user.followers.count(),
            'title': e.name,
            'avatar': avatar,
            'description': e.description,
            'lat': e.latitude,
            'long': e.longitude,
            'image_link': e.image_link,
            'when': e.when.strftime("%B %d, %Y %H:%M")
        }
        return jsonify(events_dic)
    else:
        return jsonify({'message': 'No events'})


@main.route('/news/like/<news_id>')
@login_required
def like(news_id):
    news = News.query.filter_by(id=int(news_id)).first()
    if news is None:
        return jsonify({'error': 'Invalid news id'})
    if current_user.is_like(news):
        return jsonify({'error': 'You already liked this'})
    current_user.like(news)
    return jsonify({'Message': 'Success'})


@main.route('/news/unlike/<news_id>')
@login_required
def unlike(news_id):
    news = News.query.filter_by(id=int(news_id)).first()
    if news is None:
        return jsonify({'error': 'Invalid news id'})
    if not current_user.is_like(news):
        return jsonify({'error': 'You do not like this'})
    current_user.unlike(news)
    return jsonify({'Message': 'Success'})
