from flask import g, session
from flask_sqlalchemy import SQLAlchemy
from app.users.models import User
from app import app

@app.before_request
def before_request():
    if session.get('user_id'):
        user = User.query.filter_by(id=session.get('user_id')).first()
        g.user = user

app.run(debug=True)