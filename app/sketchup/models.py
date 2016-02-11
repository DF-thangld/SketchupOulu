import datetime
import json

from flask.ext.babel import format_datetime

from app import db
from app import utilities
import sqlalchemy

class BuildingModel(db.Model):

    __tablename__ = 'custom_models'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    owner = db.relationship("User")
    is_base_item = db.Column(db.SmallInteger, default=0, index=True)
    created_time = db.Column(db.DateTime, index=True)
    file_type = db.Column(db.String(50))
    data_file = db.Column(db.String(80))
    addition_information = db.Column(db.String())
    description = db.Column(db.String())
    comment_topic_id = db.Column(db.Integer, db.ForeignKey('comment_topics.id'), index=True)
    comment_topic = db.relationship("CommentTopic")

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, BuildingModel):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not (self == other)

    def can_edit(self, user):
        if user == self.owner:
            return True
        if user.is_admin():
            return True

        return False

    def __init__(self, name='', data_file='', owner=None, addition_information='', description=''):
        self.id = utilities.generate_random_string(50)
        self.name = name
        self.data_file = data_file
        self.owner = owner
        self.addition_information = addition_information
        self.description = description
        self.created_time = datetime.datetime.now()
        self.comment_topic = CommentTopic('Comments for building model id ' + self.id, owner, 'building_model')

    def to_dict(self, include_owner=False, include_comments=False):
        owner = None
        if include_owner:
            owner = self.owner.to_dict()

        comments = None
        if include_comments:
            comments = self.comment_topic.to_dict()['comments']

        return {'id': self.id,
                'name': self.name,
                'owner': owner,
                'comments': comments,
                'created_time': format_datetime(self.created_time),
                'data_file': self.data_file,
                'file_type': self.file_type,
                'addition_information': json.loads(self.addition_information),
                'description': self.description,
                'is_base_item': self.is_base_item}

    def __repr__(self):
        return '<BuildingModel %r>' % (self.name)

class Scenario(db.Model):

    __tablename__ = 'scenarios'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    owner = db.relationship("User", primaryjoin="Scenario.owner_id == User.id")
    created_time = db.Column(db.DateTime, index=True)
    last_edited_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_edited_user = db.relationship("User", primaryjoin="Scenario.last_edited_user_id == User.id")
    last_edited_time = db.Column(db.DateTime)
    data_file = db.Column(db.String(80))
    addition_information = db.Column(db.String())
    description = db.Column(db.String())
    is_base_scenario = db.Column(db.SmallInteger, default=0, index=True)
    is_public = db.Column(db.SmallInteger, default=1, index=True)
    comment_topic_id = db.Column(db.Integer, db.ForeignKey('comment_topics.id'), index=True)
    comment_topic = db.relationship("CommentTopic")

    def __init__(self, name, owner, addition_information, data_file='', description='', is_public=1):
        self.id = utilities.generate_random_string(50)
        self.name = name
        self.owner = owner
        self.data_file = data_file
        self.addition_information = addition_information
        self.description = description
        self.is_public = is_public
        self.created_time = datetime.datetime.now()
        self.comment_topic = CommentTopic('Comments for scenario id ' + self.id, owner, 'scenario')

    def can_access(self, user):
        if user is None:
            return False
        if user == self.owner:
            return True
        if user.is_admin():
            return True
        if self.is_public == 1:
            return True

        #TODO: colaborators
        return False

    def can_edit(self, user):
        if user is None:
            return False
        if user == self.owner:
            return True
        if user.is_admin():
            return True

        #TODO: colaborators
        return False

    def to_dict(self, include_owner=False, include_last_edited_user=False, include_comments=False):
        owner = None
        if include_owner:
            owner = self.owner.to_dict()

        last_edited_user = None
        if include_last_edited_user:
            if self.last_edited_user is not None:
                last_edited_user = self.last_edited_user.to_dict()

        comments = None
        if include_comments:
            comments = self.comment_topic.to_dict()['comments']

        if self.addition_information == '':
            self.addition_information = '{}'

        return {'id': self.id,
                'name': self.name,
                'owner': owner,
                'created_time': self.created_time.isoformat(),
                'last_edited_user': last_edited_user,
                'last_edited_time': utilities.format_datetime(self.last_edited_time),
                'data_file': self.data_file,
                'addition_information': self.addition_information,
                'description': self.description,
                'is_public': self.is_public,
                'is_base_scenario': self.is_base_scenario,
                'comments': comments}

    def __repr__(self):
        return '<Scenario %r>' % (self.name)

class CommentTopic(db.Model):
    __tablename__ = 'comment_topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship("User", primaryjoin="CommentTopic.owner_id==User.id")
    created_time = db.Column(db.DateTime)
    is_suggestion = db.Column(db.SmallInteger, default=0)
    comment_type = db.Column(db.String(20))
    total_page = 0
    current_page = 0

    def __init__(self, title, owner, comment_type, is_suggestion=0):
        self.title = title
        self.owner = owner
        self.is_suggestion = is_suggestion
        self.comment_type = comment_type
        self.created_time = datetime.datetime.now()

    def get_latest_comments(self, page=1, page_size=20, return_dict=False):
        query = Comment.query.filter(Comment.topic==self).order_by(Comment.created_time.desc())
        page_data = query.paginate(page, 20, False)
        self.total_page = page_data.pages
        self.current_page = page
        if not return_dict:
            return page_data.items
        else:
            comments = []
            for comment in page_data.items:
                comments.append(comment.to_dict(include_owner=True))
            return comments

    def to_dict(self, include_owner=False):
        owner = None
        if include_owner:
            owner = self.owner.to_dict()
        comment_objects = self.get_latest_comments()
        comments = []
        for comment_object in comment_objects:
            comments.append(comment_object.to_dict(include_owner=True))

        return {'id': self.id,
                'title': self.title,
                'owner': owner,
                'created_time': self.created_time.isoformat(),
                'comments': comments}

    def __repr__(self):
        return '<CommentTopic %r>' % (self.title)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('comment_topics.id'), index=True)
    topic = db.relationship("CommentTopic")
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship("User", primaryjoin="Comment.owner_id == User.id")
    created_time = db.Column(db.DateTime)
    last_edited_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_edited_user = db.relationship("User", primaryjoin="Comment.last_edited_user_id == User.id")
    last_edited_time = db.Column(db.DateTime)

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
                'created_time': utilities.format_datetime(self.created_time),
                'content': self.content}

    def __repr__(self):
        return '<Comment %r>' % (self.id)