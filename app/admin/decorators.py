from functools import wraps
from flask.ext.babel import gettext

from flask import g, flash, redirect, url_for, request

def requires_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in g or g.user is None or not g.user.is_admin():
            flash(gettext(u'You don\'t have privilege to view this page.'))
            return redirect(url_for('page_not_found'))
        return f(*args, **kwargs)
    return decorated_function