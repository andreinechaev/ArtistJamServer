__author__ = 'faradey'


from app import create_app
# from app.models import Role

application = create_app('production')
application.config['SECRET_KEY'] = '79cc1336-0d31-11e5-a5d2-10ddb1e2ba3a'

# fan = Role(name='fan')
# artist = Role(name='artist')

if __name__ == '__main__':
    application.run()
