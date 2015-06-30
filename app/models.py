__author__ = 'faradey'

from datetime import datetime

from app import db
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


likes = db.Table('likes',
                 db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                 db.Column('news_id', db.Integer, db.ForeignKey('news.id')))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r' % self.name

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    profile = db.relationship('Profile', uselist=False, backref=db.backref('user', lazy='joined'))
    events = db.relationship('Event', backref='user', lazy='dynamic')
    news = db.relationship('News', backref='user', lazy='dynamic')
    likes = db.relationship('News', secondary=likes,
                            backref=db.backref('like', lazy='dynamic'),
                            lazy='dynamic')
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

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def like(self, news):
        if not self.is_like(news):
            self.likes.append(news)
            return self

    def unlike(self, news):
        if self.is_like(news):
            self.likes.remove(news)
            return self

    def is_like(self, news):
        return self.likes.filter(likes.c.news_id == news.id).count() > 0

    def has_profile(self):
        return self.profile is not None


from app import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    image_link = db.Column(db.String(256), unique=True)
    full_name = db.Column(db.String(256), index=True)
    show_full_name = db.Column(db.Boolean)
    about = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Profile> %r' + self.id


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

    def count_likes(self):
        return self.like.count()
