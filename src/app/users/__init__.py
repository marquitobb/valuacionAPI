import datetime
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError 
import newrelic.agent

from app.users.controllers import create_user, all_users, delete_user, get_user_by_email, get_user_by_id, change_email_or_password
from app.utils.validators import check_email
from app.utils.permissions import check_user_type

users = Blueprint('users', __name__, url_prefix='/users')

@users.route('/', methods=['POST'])
def post_index():
    if request.get_json():
        try:
            if check_email(request.json['email']):
                if create_user(request.json['email'],request.json['password'],request.json['dateOfBirth']):
                    if "type" in request.json:
                        if request.json['type'] == 'jerry':
                            u = get_user_by_email(request.json['email'])
                            if u:
                                data = {
                                    "user_id": str(u.id),
                                    "name": request.json['name'],
                                    "first_lastname": request.json['first_lastname'],
                                    "second_lastname": request.json['second_lastname'],
                                    "phone": request.json['phone'],
                                    "dob": request.json['dateOfBirth'],
                                    "avatar": request.json['avatar'],
                                    "address": request.json['address'] if 'addres' in request.json else None,
                                    }
                                headers = {'content-type': 'application/json'}
                                r = requests.post('http://magneton:5000/', json=data, headers=headers)
                                r_json = r.json()
                                if r.status_code == 201:
                                    expires = datetime.timedelta(days=1)
                                    access_token = create_access_token(identity=u.id, fresh=True,expires_delta=expires)
                                    refresh_token = create_refresh_token(u.id)
                                    response = {
                                        'success': True,
                                        'user': {
                                            'id': u.id,
                                            'name': request.json['name'],
                                            'first_lastname': request.json['first_lastname'],
                                            'second_lastname': request.json['second_lastname'],
                                            'email': u.email,
                                            'phone': request.json['phone'],
                                            'dateOfBirth': request.json['dateOfBirth'],
                                            'avatar': request.json['avatar'],
                                            'rfc': r_json['expedient']['rfc'],
                                            'address': r_json['expedient']['address'],
                                            'is_customer': r_json['expedient']['is_customer'],
                                            'progress': r_json['expedient']['progress'],
                                            },
                                        'access_token': access_token,
                                        'refresh_token': refresh_token
                                    }
                                    return response, 201
                                else:
                                    return jsonify(success=False, error_message=r_json['error_message'], error_code=1005), 400
                            else:
                                return jsonify(success=False, error_message="No se pudo recuperar el usuario", error_code=1004), 400
                    return jsonify(success=True), 201
                else:
                    return jsonify(success=False, error_message="No es posible usar ese correo electrónico", error_code=1003), 400
            else:
                return jsonify(success=False, error_message="El correo electrónico ingresado no es valido.", error_code=1002), 400
        except IntegrityError:
            newrelic.agent.record_exception()
            return jsonify(success=False, error_code=1001), 400
    else:
        return jsonify(success=False, error_code=1000), 400

@users.route('/', methods=['GET'])
@jwt_required
def get_index():
    user = get_jwt_identity()
    response = []
    if check_user_type(user,'rick'):
        users = all_users()
        for u in users:
            response.append(
                {
                    'id': u.id,
                    'email': u.email,
                }
            )
    return jsonify(response), 200

@users.route('/<user_id>', methods=['PUT'])
@jwt_required
def put_user(user_id):
    user = get_jwt_identity()
    if request.get_json():
        try:
            u = get_user_by_id(user_id)
            if u:
                if user == user_id or check_user_type(user,'rick'):
                    success = False
                    successExpedient = False
                    
                    if change_email_or_password(user_id,request.json):
                        success = True
                        
                    
                    data = {
                        "name": request.json['name'] if 'name' in request.json else None,
                        "first_lastname": request.json['first_lastname'] if 'first_lastname' in request.json else None,
                        "second_lastname": request.json['second_lastname'] if 'second_lastname' in request.json else None,
                        "phone": request.json['phone'] if 'phone' in request.json else None,
                        "dob": request.json['dateOfBirth'] if 'dateOfBirth' in request.json else None,
                        "avatar": request.json['avatar'] if 'avatar' in request.json else None,
                        "address": request.json['address'] if 'address' in request.json else None,
                        }
                    headers = {'content-type': 'application/json'}
                    r = requests.put('http://magneton:5000/{}'.format(user_id), json=data, headers=headers)
                    r_json = r.json()

                    if r.status_code == 200:
                        successExpedient = True
                    
                    u = get_user_by_id(user_id)
                    if success and successExpedient:
                        response = {
                                    'success': success,
                                    'user': {
                                        'id': u.id,
                                        'email': u.email,
                                        'name': r_json['expedient']['name'],
                                        'first_lastname': r_json['expedient']['first_lastname'],
                                        'second_lastname': r_json['expedient']['second_lastname'],
                                        'phone': r_json['expedient']['phone'],
                                        'dateOfBirth': r_json['expedient']['dob'],
                                        'avatar': str(r_json['expedient']['avatar']),
                                        'rfc': r_json['expedient']['rfc'],
                                        'address': r_json['expedient']['address'],
                                        'is_customer': r_json['expedient']['is_customer'],
                                        'progress': r_json['expedient']['progress'],
                                        }
                                }
                    elif success and not successExpedient:
                        response = {
                                    'success': success,
                                    'user': {
                                        'id': u.id,
                                        'email': u.email
                                        }
                                }
                    else:
                        response = {'success': success}

                    return response, 200
                else:
                    return jsonify(success=False, error_code=1002, error_message='No tienes los privilegios para editar esta información'), 401
            else:
                    return jsonify(success=False, error_code=1001), 400
        except IntegrityError:
            newrelic.agent.record_exception()
            return jsonify(success=False, error_code=1001), 400
    else:
        return jsonify(success=False, error_code=1000), 400

@users.route('/<user_id>', methods=['DELETE'])
@jwt_required
def delete_user_url(user_id):
    user = get_jwt_identity()
    try:
        if user == user_id or check_user_type(user,'rick'):
            if delete_user(user_id):
                return jsonify(success=True), 200
            else:
                return jsonify(success=False, error_code=1002), 400
        else:
            return jsonify(success=False, error_code=1001, error_message='No tienes los privilegios para editar esta información'), 401
    except IntegrityError:
        newrelic.agent.record_exception()
        return jsonify(success=False, error_code=1000), 400
