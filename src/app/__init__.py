from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.exceptions import HTTPException, InternalServerError
import newrelic.agent

from app.database import db_session
from app.users import users
#from app.auth import auth
#from app.expedients import expedients
#from app.buro import buro
#from app.faq import faq
#from app.quickbase import quickbase
#from app.savings import savings

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)

    jwt = JWTManager(app)

    #app.register_blueprint(auth)
    app.register_blueprint(users)
    #app.register_blueprint(expedients)
    #app.register_blueprint(buro)
    #app.register_blueprint(faq)
    #app.register_blueprint(quickbase)
    #app.register_blueprint(savings)

    @app.route("/")
    def hello_world():
        return jsonify(hello="world")

    @app.errorhandler(Exception)
    def handle_exception(e):
        newrelic.agent.record_exception()
        return jsonify(success=False, error_message="{}".format(e)), 500

    @app.errorhandler(HTTPException)
    def handle_bad_request(e):
        newrelic.agent.record_exception()
        return jsonify(success=False, error_message="{}".format(e)), e.code
    
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
