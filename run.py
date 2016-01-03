from flask import g, session
from flask_sqlalchemy import SQLAlchemy
from app.users.models import User
from app import app

@app.before_request
def before_request():
    if session.get('user_id'):
        user = User.query.filter_by(id=session.get('user_id')).first()
        if user is not None:
            g.user = user

app.config['SERVER_NAME'] = 'localhost:5000'
app.run(debug=True)