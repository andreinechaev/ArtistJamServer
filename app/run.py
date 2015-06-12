__author__ = 'faradey'


from app import create_app

application = create_app('production')
application.config['SECRET_KEY'] = '79cc1336-0d31-11e5-a5d2-10ddb1e2ba3a'

# fan = Role(name='fan')
# artist = Role(name='artist')
#
# with app.app_context():
#     db.create_all()
#     db.session.add_all([fan, artist])
#     db.session.commit()

if __name__ == '__main__':
    application.run()