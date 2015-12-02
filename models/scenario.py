from variables import db

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_time = db.Column(db.DateTime)
    last_edited_time = db.Column(db.DateTime)
    data_file = db.Column(db.String(80), unique=False)
    addition_information = db.Column(db.Text())
    description = db.Column(db.Text())

    def __init__(self, name, owner_id, created_time, last_edited_time, data_file, addition_information, description):
        self.name = name
        self.owner_id = owner_id
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.data_file = data_file
        self.addition_information = addition_information
        self.description = description

    def __repr__(self):
        return '<Scenario %r>' % self.name