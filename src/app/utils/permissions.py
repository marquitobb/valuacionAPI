from app.database import db_session
from app.users.models import User, UserType

def cast_user_type(user_type):
    if user_type == 'rick':
        return UserType.rick
    elif user_type == 'morty':
        return UserType.morty
    elif user_type == 'beth':
        return UserType.beth
    elif user_type == 'summer':
        return UserType.summer
    elif user_type == 'jerry':
        return UserType.jerry

def get_user_info(user_id):
    return db_session.query(User).get(user_id)
    
def check_user_type(user_id, user_type):
    u = db_session.query(User).get(user_id)
    return (u and u.user_type == cast_user_type(user_type))
    
    
