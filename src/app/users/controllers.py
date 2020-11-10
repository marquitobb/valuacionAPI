import datetime
import pytz
import sys
import string
import random
import requests
sys.path = ['', '..'] + sys.path[1:]

from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm.exc import NoResultFound 

from app.users.models import User
from app.database import db_session

tz = pytz.timezone('America/Mexico_City')

def all_users():
    try:
        return db_session.query(User).all()
    except NoResultFound:
        return None

def create_user(email,password,dob):
    try:
        prev = db_session.query(User).filter_by(email=email).one()
        return False
    except NoResultFound:
        passwd = password.strip()
        if password == 'Pass2020' and dob == '1900-01-01':
            passwd = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=8))
            send_email_password(email, passwd)

        u = User(email=email.strip(),password=str(passwd).encode('utf-8'))
        db_session.add(u)
        db_session.commit()
        return True

def delete_user(user_id):
    try:
        u = db_session.query(User).filter_by(id=user_id).first()
        if not u.is_deleted():
            u.deleted_at = datetime.datetime.now(tz=tz)
            u.is_blocked = 1
            db_session.commit()
        return True
    except NoResultFound:
        return False

def get_user_by_email(email):
    try:
        return db_session.query(User).filter_by(email=email).first()
    except NoResultFound:
        return None

def get_user_by_id(user_id):
    try:
        return db_session.query(User).filter_by(id=user_id).first()
    except NoResultFound:
        return None

def change_email_or_password(user_id,data):
    try:
        u = db_session.query(User).filter_by(id=user_id).first()
        u.update(**data)
        db_session.commit()
        return True
    except:
        return False

def send_email_password(email, password):
    try:
        data = {
            "fromPlatform": "mewtwo",
            "template": "mewtwo_login_lp",
            "subject": "Alta de cuenta",
            "from": "no-reply@curadeuda.com",
            "fromName": "Cura Deuda",
            "to": email,
            "message": "",
            "personalization":{
                "password": password,
            }
        }
        headers = {'content-type': 'application/json'}
        r = requests.post('http://pidgeot:5000/mailing', json=data, headers=headers)
        r_json = r.json()
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False