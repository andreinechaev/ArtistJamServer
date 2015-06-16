__author__ = 'faradey'


from app import create_app
from flask import jsonify
# from app.models import Role

application = create_app('production')
application.config['SECRET_KEY'] = '79cc1336-0d31-11e5-a5d2-10ddb1e2ba3a'

# fan = Role(name='fan')
# artist = Role(name='artist')

@application.errorhandler(500)
def error_handler():
    return jsonify({"error": "Error occurred  on the server"}), 500

@application.errorhandler(404)
def page_not_found():
    return jsonify({"error": "Page not found"}), 404


if __name__ == '__main__':
    application.run()
