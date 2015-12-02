from variables import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), unique=False)
    username = db.Column(db.String(80), unique=True)
    fullname = db.Column(db.String(80), unique=False)
    email = db.Column(db.String(120), unique=True)
    address = db.Column(db.String(80), unique=False)
    postal_code = db.Column(db.String(80), unique=False)
    phone_number = db.Column(db.String(80), unique=False)
    birthdate = db.Column(db.DateTime)

    def __init__(self, username, email, password, fullname, address='', postal_code='', phone_number='', birthdate=None):
        self.username = username
        self.email = email
        self.password = password
        
        self.fullname = fullname
        self.address = address
        self.postal_code = postal_code
        self.phone_number = phone_number
        self.birthdate = birthdate

    def __repr__(self):
        return '<User %r>' % self.username