from variables import db
import datetime

class CommentTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_time = db.Column(db.DateTime)
    is_suggestion = db.Column(db.Boolean)

    def __init__(self, title, owner_id, created_time=datetime.datetime.now(), is_suggestion=False):
        self.title = name
        self.owner_id = owner_id
        self.created_time = created_time
        self.is_suggestion = is_suggestion

    def __repr__(self):
        return '<Comment %r>' % self.title

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('comment_topic.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_time = db.Column(db.DateTime)
    content = db.Column(db.String(1000), unique=False)

    def __init__(self, name, owner_id, content,created_time=datetime.datetime.now()):
        self.name = name
        self.owner_id = owner_id
        self.created_time = created_time
        self.content = content
        

    def __repr__(self):
        return '<Comment %r>' % self.id