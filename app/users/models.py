from app.users import constants as USER
from app import db
import sqlalchemy

class User(db.Model):

    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True) 
    username = sqlalchemy.Column(sqlalchemy.String(80), unique=True) 
    email = sqlalchemy.Column(sqlalchemy.String(120), unique=True) 
    password = sqlalchemy.Column(sqlalchemy.String(80))
    address = sqlalchemy.Column(sqlalchemy.String(80))
    postal_code = sqlalchemy.Column(sqlalchemy.String(80))
    phone_number = sqlalchemy.Column(sqlalchemy.String(80))
    
    birthdate = sqlalchemy.Column(sqlalchemy.DateTime)
    last_login = sqlalchemy.Column(sqlalchemy.DateTime)
    last_activity = sqlalchemy.Column(sqlalchemy.DateTime)
    last_login_attempt = sqlalchemy.Column(sqlalchemy.DateTime)
    
    verification_code = sqlalchemy.Column(sqlalchemy.String(80))
    login_attempts = sqlalchemy.Column(sqlalchemy.Integer)
    banned = sqlalchemy.Column(sqlalchemy.SmallInteger, default=0)

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password


    def __repr__(self):
        return '<User %r>' % (self.name)