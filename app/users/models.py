from app.users import constants as USER
from app import db
import sqlalchemy

user_to_group = db.Table('user_to_group',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    address = db.Column(db.String(80), default='')
    postal_code = db.Column(db.String(80), default='')
    phone_number = db.Column(db.String(80), default='')
    fullname = db.Column(db.String(80), default='')
    
    birthdate = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime)
    last_login_attempt = db.Column(db.DateTime)
    
    verification_code = db.Column(db.String(80))
    login_attempts = db.Column(db.Integer, default=0)
    banned = db.Column(db.SmallInteger, default=0)
    login_token = db.Column(db.String(50), default='')

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(200), default='')

    def __init__(self, name='', description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Group %r>' % (self.name)