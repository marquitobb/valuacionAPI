import enum
import uuid
import hashlib
import datetime
import pytz
import random
import string

from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from werkzeug.security import generate_password_hash

from app.database import Base, db_session

tz = pytz.timezone('America/Mexico_City')

class UserType(enum.Enum):
    rick = 0
    morty = 1
    beth = 2
    summer = 3
    jerry = 4

class User(Base):
    __tablename__ = 'users'
    id = Column(UUIDType(binary=False), primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(120))
    user_type = Column(Enum(UserType))
    last_login = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean,default=False)
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))
    updated_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz),onupdate=datetime.datetime.now(tz=tz))
    deleted_at = Column(DateTime, nullable=True)
    recovery_token = relationship("RecoveryToken", back_populates="user")
    
    def __init__(self, email=None, password=None, user_type=UserType.jerry):
        self.id = uuid.uuid4()
        self.email = email
        self.password = generate_password_hash(password)
        self.user_type = user_type
        self.created_at = datetime.datetime.now(tz=tz)
        self.updated_at = datetime.datetime.now(tz=tz)

    def __repr__(self):
        return '<User %r>' % (self.email)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'password':
                    if value is not None:
                        setattr(self, key, generate_password_hash(value))
                else:
                    if value is not None:
                        setattr(self, key, value)
                self.updated_at = datetime.datetime.now(tz=tz)

    def update_last_login(self):
        self.last_login = datetime.datetime.now(tz=tz)
        db_session.commit()
    
    def change_password(self,secret):
        self.password = generate_password_hash(secret)
        self.updated_at = datetime.datetime.now(tz=tz)
        db_session.commit()
    
    def is_active(self):
        return (self.is_blocked == 0 and self.deleted_at == None)
    
    def is_deleted(self):
        return (self.deleted_at != None)

class RecoveryToken(Base):
    __tablename__ = 'users_recovery_token'
    id = Column(UUIDType(binary=False), primary_key=True)
    token = Column(String(60))
    user_id = Column(UUIDType(binary=False), ForeignKey('users.id'))
    user = relationship("User", back_populates="recovery_token")
    is_used = Column(Boolean,default=False)
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))
    expired_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz)+datetime.timedelta(hours=12))
    deleted_at = Column(DateTime, nullable=True)
    
    def __init__(self, user_id=None):
        self.id = uuid.uuid4()
        self.token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=60))
        self.user_id = user_id
        self.created_at = datetime.datetime.now(tz=tz)
        self.updated_at = datetime.datetime.now(tz=tz)
    
    def is_active(self):
        return (self.expired_at.replace(tzinfo=tz) > datetime.datetime.now(tz=tz).replace(tzinfo=tz) and self.is_used == 0 and self.deleted_at == None)
    
    def is_deleted(self):
        return (self.deleted_at != None)
