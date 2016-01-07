from flask import g, session
from flask_sqlalchemy import SQLAlchemy
from app.users.models import User
from app import app

@app.before_request
def before_request():
    if session.get('user_id'):
        user = User.query.filter_by(id=session.get('user_id')).first()
        g.user = user
    else:
        g.user = None

#app.config['SERVER_NAME'] = '127.0.0.1:5000'
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)