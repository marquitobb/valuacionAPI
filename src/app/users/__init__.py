import datetime
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError 
import newrelic.agent

#from app.users.controllers import create_user, all_users, delete_user, get_user_by_email, get_user_by_id, change_email_or_password
#from app.utils.validators import check_email
#from app.utils.permissions import check_user_type

users = Blueprint('users', __name__, url_prefix='/users')

@users.route('/', methods=['POST'])
def get_users():
    return 'users'