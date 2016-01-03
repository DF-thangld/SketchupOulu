import datetime

from app import db
from app.users.models import User
import sqlalchemy

class JournalCategory(db.Model):

    __tablename__ = 'journal_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(500), unique=True)
    is_activated = db.Column(db.SmallInteger, default=1)
    total_page = 0
    current_page = 0

    def __init__(self, name='', description=''):
        self.name = name
        self.description = description

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description}

    def get_journals(self, page=1, filter=''):
        if filter != '':
            query = Journal.query.filter(Journal.category==self).filter(Journal.title.like('%'+filter+'%')).order_by(Journal.post_time.desc())
        else:
            query = Journal.query.filter(Journal.category==self).order_by(Journal.post_time.desc())

        page_data = query.paginate(page, 20, False)
        self.total_page = page_data.pages
        self.current_page = page
        return page_data.items

    def __repr__(self):
        return '<JournalCategory %r>' % (self.name)

class Journal(db.Model):

    __tablename__ = 'journals'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey('journal_categories.id'))
    category = db.relationship("JournalCategory")
    created_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_user = db.relationship("User", primaryjoin="Journal.created_user_id == User.id")
    last_edited_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_edited_user = db.relationship("User", primaryjoin="Journal.last_edited_user_id == User.id")
    post_time = db.Column(db.DateTime)
    last_edited_time = db.Column(db.DateTime)
    is_activated = db.Column(db.SmallInteger, default=1)

    def __init__(self, title, content, created_user, category, is_activated=1):
        self.title = title
        self.content = content
        self.created_user = created_user
        self.is_activated = is_activated
        self.category = category
        self.post_time = datetime.datetime.now()

    def to_dict(self, include_category=False, include_created_user=False, include_last_edited_user=False):
        category = None
        if include_category:
            category = self.category.to_dict()
        created_user = None
        if include_created_user:
            created_user = self.created_user.to_dict()
        last_edited_user = None
        if include_last_edited_user:
            if self.last_edited_user is not None:
                last_edited_user = self.last_edited_user.to_dict()

        return {'id': self.id,
                'title': self.title,
                'content': self.content,
                'is_activated': self.is_activated,
                'category': category,
                'created_user': created_user,
                'post_time': self.post_time,
                'last_edited_user': last_edited_user,
                'last_edited_time': self.last_edited_time}

    def __repr__(self):
        return '<Journal %r>' % (self.title)