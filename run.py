import datetime

from flask import g, session, request, make_response
from app.users.models import User, UserSession
from app import app, db

@app.before_request
def before_request():
    g.user = None
    if session.get('user_id'):
        user = User.query.filter_by(id=session.get('user_id')).first()
        g.user = user
        return

    #check cookie for session
    session_id = request.cookies.get('session_id')
    if session_id is None or session_id == '':
        return

    #session found, attempt login by session
    session_info = session_id.split('|')
    user_id = int(session_info[0])
    token = session_info[1]
    user_session = UserSession.query.filter(UserSession.user_id==user_id, UserSession.token==token).first()
    if user_session is None:
        response = make_response()
        response.set_cookie('session_id', '', expires=0)
        return response

    db.session.delete(user_session)
    db.session.commit()
    user = User.query.filter_by(id=user_id).first()
    if user is not None and user_session.expired_time >= datetime.datetime.now():
        new_user_session = UserSession(user.id)
        db.session.add(new_user_session)
        db.session.commit()
        g.user = user
        session['user_id'] = user.id

        cookie_value = str(user.id) + '|' + new_user_session.token
        response = make_response()
        response.set_cookie('session_id', cookie_value, expires=datetime.datetime.now() + datetime.timedelta(days=5))
        return
    else:
        response = make_response()
        response.set_cookie('session_id', '', expires=0)
        return




#app.config['SERVER_NAME'] = '127.0.0.1:5000'
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)