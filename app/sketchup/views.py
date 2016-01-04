import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.uploads import UploadSet, IMAGES

from app import db, send_mail, upload_picture
from app.users.forms import RegisterForm, LoginForm, UserProfileForm, ResetPasswordForm
from app.users.models import User
from app.sketchup.models import Scenario, BuildingModel, Comment, CommentTopic
import app.utilities as utilities

mod = Blueprint('sketchup', __name__, url_prefix='/sketchup')

@mod.route('/view_scenario/')
def view_scenario():
    scenario_id=request.args.get('id', '')
    if scenario_id == '':
        return render_template('404.html'), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return render_template('404.html'), 404

    if scenario.is_public == 0 and not scenario.owner == g.user and not g.user.is_admin():
        return render_template('404.html'), 404

    return render_template("sketchup/view_scenario.html", scenario=scenario.to_dict(include_owner=True, include_last_edited_user=True, include_comments=True))

@mod.route('/get_scenario/')
def get_scenario():
    errors = []
    scenario_id=request.args.get('id', '')
    if scenario_id == '':
        return json.dumps(['Scenario not found']), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps(['Scenario not found']), 404

    if scenario.is_public == 0 and not scenario.owner == g.user and not g.user.is_admin():
        return json.dumps(['Scenario not found']), 404

    return json.dumps(scenario.to_dict(include_owner=True, include_last_edited_user=True, include_comments=True))