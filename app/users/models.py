from app.users import constants as USER
from app import db
import sqlalchemy

user_to_group = db.Table('user_to_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

class User(db.Model):

    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True) 
    username = sqlalchemy.Column(sqlalchemy.String(80), unique=True)
    email = sqlalchemy.Column(sqlalchemy.String(120), unique=True) 
    password = sqlalchemy.Column(sqlalchemy.String(80))
    address = sqlalchemy.Column(sqlalchemy.String(80))
    postal_code = sqlalchemy.Column(sqlalchemy.String(80))
    phone_number = sqlalchemy.Column(sqlalchemy.String(80))
    fullname = sqlalchemy.Column(sqlalchemy.String(80))
    
    birthdate = sqlalchemy.Column(sqlalchemy.DateTime)
    last_login = sqlalchemy.Column(sqlalchemy.DateTime)
    last_activity = sqlalchemy.Column(sqlalchemy.DateTime)
    last_login_attempt = sqlalchemy.Column(sqlalchemy.DateTime)
    
    verification_code = sqlalchemy.Column(sqlalchemy.String(80))
    login_attempts = sqlalchemy.Column(sqlalchemy.Integer)
    banned = sqlalchemy.Column(sqlalchemy.SmallInteger, default=0)

    groups = db.relationship('Group', secondary=user_to_group,
        backref=db.backref('groups', lazy='dynamic'))

    def __init__(self, username='', email='', password=''):
        self.username = username
        self.email = email
        self.password = password

    def is_admin(self):
        for group in self.groups:
            if group.id == 1:
                return True
        return False


    def __repr__(self):
        return '<User %r>' % (self.username)

class Group(db.Model):

    __tablename__ = 'groups'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(80), unique=True)
    description = sqlalchemy.Column(sqlalchemy.String(200), unique=True)

    def __init__(self, name='', description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Group %r>' % (self.name)