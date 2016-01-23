import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.uploads import UploadSet, IMAGES

from app import db, send_mail, upload_picture
from app.users.forms import RegisterForm, LoginForm, UserProfileForm, ResetPasswordForm
from app.users.models import User
from app.sketchup.models import Scenario, BuildingModel, Comment, CommentTopic
import app.utilities as utilities
from app.users.decorators import requires_login

mod = Blueprint('sketchup', __name__, url_prefix='/sketchup')

@mod.route('/view_scenario/')
def view_scenario():
    scenario_id=request.args.get('id', '')
    if scenario_id == '':
        return render_template('404.html'), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return render_template('404.html'), 404

    if scenario.is_public == 0:
        if g.user is None:
            return render_template('404.html'), 404
        elif not g.user.is_admin() and not scenario.owner == g.user:
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

    if not scenario.can_access(g.user):
        return json.dumps(['Scenario not found']), 404

    return json.dumps(scenario.to_dict(include_owner=True, include_last_edited_user=True, include_comments=True))

@mod.route('/update_scenario/<scenario_id>', methods=['POST'])
def update_scenario(scenario_id):
    errors = []
    if scenario_id == '':
        return json.dumps(['Scenario not found']), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps(['Scenario not found']), 404

    if not scenario.can_edit(g.user):
        return json.dumps(['Scenario not found']), 404

    scenario_name = request.form.get('scenario_name', '')
    is_public = request.form.get('is_public', 1)
    if scenario_name == '':
        errors.append('Scenario name cannot be blank')
    if len(errors) > 0:
        return json.dumps(errors), 400

    scenario.name = scenario_name
    scenario.is_public = is_public
    db.session.commit()

    return json.dumps({
        'success': True
    }), 200