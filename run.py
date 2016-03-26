# -*- coding: utf-8 -*-
import datetime

from flask import g, session, request, make_response
from flask_sqlalchemy import SQLAlchemy
from app.users.models import User, UserSession
from app import app, db
import config

@app.before_request
def before_request():
    g.user = None
    if session.get('user_id'):
        user = User.query.filter_by(id=session.get('user_id')).first()
        g.user = user
        if 'locale' in session and g.user.default_locale != session['locale']:
            g.user.default_locale = session['locale']
            db.session.commit()
        elif 'locale' not in session:
            session['locale'] = g.user.default_locale
    else:
        #check cookie for session
        session_id = request.cookies.get('session_id')
        if session_id is not None and session_id != '':
            #session found, attempt login by session
            session_info = session_id.split('|')
            user_id = int(session_info[0])
            token = session_info[1]
            user_session = UserSession.query.filter(UserSession.user_id==user_id, UserSession.token==token).first()
            if user_session is None:
                g.sketchup_cookie_action = {'action': 'remove_cookie', 'parameter': {'id': 'session_id', 'value': ''}}
            elif user_session is not None:
                db.session.delete(user_session)
                db.session.commit()
                user = User.query.filter_by(id=user_id).first()
                if user is not None and user.banned != 1 and user_session.expired_time >= datetime.datetime.now():
                    new_user_session = UserSession(user.id)
                    db.session.add(new_user_session)
                    db.session.commit()
                    g.user = user
                    session['user_id'] = user.id
                    cookie_value = str(user.id) + '|' + new_user_session.token
                    g.sketchup_cookie_action = {'action': 'add_cookie', 'parameter': {'id': 'session_id', 'value': cookie_value}}
                else:
                    g.sketchup_cookie_action = {'action': 'remove_cookie', 'parameter': {'id': 'session_id', 'value': ''}}


@app.after_request
def call_after_request_callbacks(response):
    action = getattr(g, 'sketchup_cookie_action', None)
    if action is not None:
        if action['action'] == 'remove_cookie':
            response.set_cookie(action['parameter']['id'], action['parameter']['value'], expires=0, path='/')
        elif action['action'] == 'add_cookie':
            response.set_cookie(action['parameter']['id'], action['parameter']['value'], expires=datetime.datetime.now() + datetime.timedelta(days=5), path='/')
    return response


#app.config['SERVER_NAME'] = '127.0.0.1:5000'
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
