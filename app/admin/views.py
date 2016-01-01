from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash

from app import db
from app.users.models import User, Group
from app.admin.decorators import requires_admin

mod = Blueprint('admin', __name__, url_prefix='/admin')

@mod.route('/user_management/')
@requires_admin
def user_management():
    return render_template("admin/user_management.html", user=g.user)