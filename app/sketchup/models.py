import datetime

from app import db
from app.users.models import User
import sqlalchemy

class BuildingModel(db.Model):

    __tablename__ = 'custom_models'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship("User")
    created_time = db.Column(db.DateTime)
    data_file = db.Column(db.String(80))
    addition_information = db.Column(db.String())
    description = db.Column(db.String())

    def __init__(self, name='', data_file='', owner=None, addition_information='', description=''):
        self.name = name
        self.data_file = data_file
        self.owner = owner
        self.addition_information = addition_information
        self.description = description
        self.created_time = datetime.datetime.now()

    def to_dict(self, include_owner=False):
        owner = None
        if include_owner:
            owner = self.owner.to_dict()
        return {'id': self.id,
                'name': self.name,
                'owner': owner,
                'addition_information': self.addition_information,
                'description': self.description}

    def __repr__(self):
        return '<BuildingModel %r>' % (self.name)

class Scenario(db.Model):

    __tablename__ = 'scenarios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship("User", primaryjoin="Scenario.owner_id == User.id")
    created_time = db.Column(db.DateTime)
    last_edited_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_edited_user = db.relationship("User", primaryjoin="Scenario.last_edited_user_id == User.id")
    last_edited_time = db.Column(db.DateTime)
    data_file = db.Column(db.String(80))
    addition_information = db.Column(db.String())
    description = db.Column(db.String())
    is_base_scenario = db.Column(db.SmallInteger, default=0)
    is_public = db.Column(db.SmallInteger, default=1)

    def __init__(self, name, owner, data_file, addition_information, description, is_public=1):
        self.name = name
        self.owner = owner
        self.data_file = data_file
        self.addition_information = addition_information
        self.description = description
        self.is_public = is_public
        self.created_time = datetime.datetime.now()

    def to_dict(self, include_owner=False, include_last_edited_user=False):
        owner = None
        if include_owner:
            owner = self.owner.to_dict()
        last_edited_user = None
        if include_last_edited_user:
            if self.last_edited_user is not None:
                last_edited_user = self.last_edited_user.to_dict()

        return {'id': self.id,
                'name': self.name,
                'owner': owner,
                'created_time': self.created_time,
                'last_edited_user': last_edited_user,
                'last_edited_time': self.last_edited_time,
                'data_file': self.data_file,
                'addition_information': self.addition_information,
                'description': self.description,
                'is_public': self.is_public}

    def __repr__(self):
        return '<Scenario %r>' % (self.name)

class CommentTopic(db.Model):
    __tablename__ = 'comment_topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship("User")
    created_time = db.Column(db.DateTime)
    is_suggestion = db.Column(db.SmallInteger, default=0)
    total_page = 0
    current_page = 0

    def __init__(self, title, owner, scenario, is_suggestion=0):
        self.title = title
        self.owner = owner
        self.scenario = scenario
        self.is_suggestion = is_suggestion
        self.created_time = datetime.datetime.now()

    def get_latest_comments(self, page=1, page_size=20):
        query = Comment.query.filter(Comment.topic==self).order_by(Comment.created_time.desc())
        page_data = query.paginate(page, 20, False)
        self.total_page = page_data.pages
        self.current_page = page
        return page_data.items

    def to_dict(self, include_owner=False, include_scenario=False):
        owner = None
        if include_owner:
            owner = self.owner.to_dict()
        scenario = None
        if include_scenario:
            scenario = self.scenario.to_dict()

        return {'id': self.id,
                'title': self.name,
                'owner': owner,
                'scenario': scenario,
                'created_time': self.created_time}

    def __repr__(self):
        return '<CommentTopic %r>' % (self.title)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship("User")
    topic_id = db.Column(db.Integer, db.ForeignKey('comment_topics.id'))
    topic = db.relationship("CommentTopic")
    created_time = db.Column(db.DateTime)
    content = db.Column(db.String(1000))

    def __init__(self, owner, topic, content):
        self.owner = owner
        self.topic = topic
        self.content = content
        self.created_time = datetime.datetime.now()

    def to_dict(self, include_owner=False, include_topic=False):
        owner = None
        if include_owner:
            owner = self.owner.to_dict()
        topic = None
        if include_topic:
            topic = self.topic.to_dict()

        return {'id': self.id,
                'owner': owner,
                'topic': topic,
                'created_time': self.created_time,
                'content': self.content}

    def __repr__(self):
        return '<Comment %r>' % (self.id)