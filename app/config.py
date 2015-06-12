__author__ = 'faradey'

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test_data.sqlite')


class ProductionConfig(Config):

    db_username = 'faraday'
    db_password = '6bb36edc-0ff4-11e5-85d9-10ddb1e2ba3a'
    db_hostname = 'ajdb.cbdzhwxehqmz.eu-west-1.rds.amazonaws.com:5432'
    db_name = 'ajdb'
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + db_username + ':' \
                              + db_password + '@' \
                              + db_hostname + '/' \
                              + db_name

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
