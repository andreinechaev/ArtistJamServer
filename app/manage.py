__author__ = 'faradey'

from app import create_app, db
from app.models import User, Profile, Event, News, Role, Follow
from flask.ext.script import Shell, Manager
from flask.ext.migrate import Migrate, MigrateCommand
# production
application = create_app('production')
application.config['SECRET_KEY'] = '79cc1336-0d31-11e5-a5d2-10ddb1e2ba3a'
manager = Manager(application)
migrate = Migrate(application, db)

def make_shell_context():
    return dict(app=application, db=db, User=User, Profile=Profile, Event=Event, News=News, Role=Role)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
