__author__ = 'faradey'


from app import create_app
from flask import jsonify

application = create_app('production')
application.config['SECRET_KEY'] = '79cc1336-0d31-11e5-a5d2-10ddb1e2ba3a'


@application.errorhandler(500)
def error_handler(error):
    return jsonify({"error": repr(error)}), 500

@application.errorhandler(404)
def page_not_found(error):
    return jsonify({"error": repr(error)}), 404


@application.errorhandler(300)
def exception_handler(error):
    return jsonify({'error': repr(error)}), 300

@application.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': repr(error)}), 405

@application.errorhandler(504)
def gateway_timeout(error):
    return jsonify({'error': repr(error)}), 504

if __name__ == '__main__':
    application.run()
