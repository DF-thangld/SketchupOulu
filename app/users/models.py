import datetime
from app import db
import app.utilities as utilities
import app.sketchup.models as sketchup
from flask.ext.babel import format_datetime

user_to_group = db.Table('user_to_group',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(80))
    address = db.Column(db.String(80), default='')
    postal_code = db.Column(db.String(80), default='')
    phone_number = db.Column(db.String(80), default='')
    fullname = db.Column(db.String(80), default='')
    birthdate = db.Column(db.DateTime)
    profile_picture = db.Column(db.String(80), default='default_profile.png')
    join_date = db.Column(db.DateTime)
    default_locale = db.Column(db.String(10), default='fi')

    last_login = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime)
    last_login_attempt = db.Column(db.DateTime)
    
    verification_code = db.Column(db.String(80), default='', index=True)
    login_attempts = db.Column(db.Integer, default=0)
    banned = db.Column(db.SmallInteger, default=0)
    login_token = db.Column(db.String(50), default='', index=True)
    password_token = db.Column(db.String(50), default='', index=True)

    groups = db.relationship('Group', secondary=user_to_group,
        backref=db.backref('groups', lazy='dynamic'))

    scenarios_total_page = 0
    scenarios_current_page = 0
    building_models_total_page = 0
    building_models_current_page = 0
    comment_topic_id = db.Column(db.Integer, db.ForeignKey('comment_topics.id', use_alter=True))
    comment_topic = db.relationship("CommentTopic",
                                    primaryjoin="User.comment_topic_id==CommentTopic.id", post_update=True)

    def __init__(self, username='', email='', password=''):
        self.join_date = datetime.datetime.now()
        self.username = username
        self.email = email
        self.password = password
        self.comment_topic = sketchup.CommentTopic('Comments for user id ' + self.username, self, 'user')

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, User):
            return self.username == other.username
        return False

    def __ne__(self, other):
        return not (self == other)

    def to_dict(self, include_group=False, include_sensitive_information=False):
        groups = None
        if include_group:
            groups = []
            for group in self.groups:
                groups.append(group.to_dict())
        if include_sensitive_information:
            return {'id': self.id,
                    'username': self.username,
                    'email': self.email,
                    'fullname': self.fullname,
                    'phone_number': self.phone_number,
                    'address': self.address,
                    'profile_picture': self.profile_picture,
                    'groups': groups}
        else:
            return {'id': self.id,
                    'username': self.username,
                    'profile_picture': self.profile_picture}

    def get_scenarios(self, filter_text='', page=1, return_dict=False, requested_user=None):
        if requested_user is None:
            requested_user = self
        if filter_text != '':
            query = sketchup.Scenario.query.filter(sketchup.Scenario.owner == self)\
                    .filter(sketchup.Scenario.name.like('%'+filter_text+'%'))
        else:
            query = sketchup.Scenario.query.filter(sketchup.Scenario.owner == self)

        if requested_user is None or (requested_user != self and not requested_user.is_admin()):
            query = query.filter(sketchup.Scenario.is_public == 1)
        query = query.order_by(sketchup.Scenario.last_edited_time.desc())\
                    .order_by(sketchup.Scenario.created_time.desc())

        page_data = query.paginate(page, 20, False)
        self.scenarios_total_page = page_data.pages
        self.scenarios_current_page = page

        if not return_dict:
            return page_data.items
        else:
            scenarios = []
            for scenario in page_data.items:
                scenarios.append(scenario.to_dict())
            return scenarios

    def get_available_building_models(self, include_base_models=True, return_dict=False):
        query = sketchup.BuildingModel.query.filter(sketchup.BuildingModel.owner==self)\
                .order_by(sketchup.BuildingModel.created_time.desc())
        building_models = query.all()

        #get pre-defined models
        if include_base_models:
            query = sketchup.BuildingModel.query.filter(sketchup.BuildingModel.is_base_item==1)\
                    .order_by(sketchup.BuildingModel.created_time.desc())
            for building_model in query.all():
                if building_model not in building_models:
                    building_models.append(building_model)

        if not return_dict:
            return building_models
        else:
            building_models_array = []
            for building_model in building_models:
                building_models_array.append(building_model.to_dict())
            return building_models_array

    def get_comments(self):
        return self.comment_topic.to_dict(include_owner=True)['comments']

    def get_building_models(self, page=1, filter_text='', return_dict=False):
        if filter_text != '':
            query = sketchup.BuildingModel.query.filter(sketchup.BuildingModel.owner==self)\
                .filter(sketchup.BuildingModel.name.like('%'+filter_text+'%'))\
                .order_by(sketchup.BuildingModel.created_time.desc())
        else:
            query = sketchup.BuildingModel.query.filter(sketchup.BuildingModel.owner==self)\
                .order_by(sketchup.BuildingModel.created_time.desc())

        page_data = query.paginate(page, 20, False)
        self.building_models_total_page = page_data.pages
        self.building_models_current_page = page

        if not return_dict:
            return page_data.items
        else:
            building_models = []
            for building_model in page_data.items:
                building_models.append(building_model.to_dict())
            return building_models

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
    name = db.Column(db.String(80), unique=True, index=True)
    description = db.Column(db.String(200), default='')

    def __init__(self, name='', description=''):
        self.name = name
        self.description = description

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description}

    def __repr__(self):
        return '<Group %r>' % (self.name)

class UserSession(db.Model):

    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    token = db.Column(db.String(100), unique=True)
    generated_time = db.Column(db.DateTime)
    expired_time = db.Column(db.DateTime)

    def __init__(self, user_id):
        self.user_id = user_id
        self.token = utilities.generate_random_string(100)
        self.generated_time = datetime.datetime.now()
        self.expired_time = self.generated_time + datetime.timedelta(days=30)

    def __repr__(self):
        return '<UserSession %r>' % (str(self.user_id))

db.Index('idx_user_token', UserSession.user_id, UserSession.token)