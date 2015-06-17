__author__ = 'faradey'

from datetime import datetime

from app import db
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    profile_id = db.relationship('Profile', uselist=False, backref='user')
    events = db.relationship('Event', backref='user', lazy='dynamic')
    news = db.relationship('News', backref='user', lazy='dynamic')
    since = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<User> %r' + self.username

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_link = db.Column(db.String(256), unique=True)
    full_name = db.Column(db.String(256), index=True)
    show_full_name = db.Column(db.Boolean)
    about = db.Column(db.Text)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(256), unique=True, index=True)
    image_link = db.Column(db.String(256), unique=True)
    description = db.Column(db.Text, index=False)
    latitude = db.Column(db.Float(8))
    longitude = db.Column(db.Float(8))
    when = db.Column(db.DateTime)
    posted = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Event> %r' + self.name

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(256), unique=True, index=True)
    image_link = db.Column(db.String(256), unique=True)
    description = db.Column(db.Text, index=False)
    posted = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<News> %r' + self.name