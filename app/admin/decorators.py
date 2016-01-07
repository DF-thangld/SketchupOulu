from functools import wraps

from flask import g, flash, redirect, url_for, request

def requires_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None and not g.user.is_admin():
            flash(u'You don\'t have privilege to view this page.')
            return redirect(url_for('users.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function