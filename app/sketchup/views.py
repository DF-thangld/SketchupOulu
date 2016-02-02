import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.uploads import UploadSet, IMAGES
from sqlalchemy.dialects import mysql

from app import db, send_mail, upload_file
from app.users.decorators import requires_login
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

    if scenario.is_public == 0:
        if g.user is None:
            return render_template('404.html'), 404
        elif not (g.user.is_admin() or scenario.owner == g.user):
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

    if scenario.is_public == 0 and not (scenario.owner == g.user or g.user.is_admin()):
        return json.dumps(['Scenario not found']), 404

    return json.dumps(scenario.to_dict(include_owner=True, include_last_edited_user=True, include_comments=True))


@mod.route('/update_scenario/<scenario_id>', methods=['POST'])
@requires_login
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
    scenario.description = request.form.get('scenario_description', scenario.description)
    db.session.commit()

    return json.dumps({
        'success': True
    }), 200


@mod.route('/delete_scenario/<scenario_id>', methods=['GET'])
@requires_login
def delete_scenario(scenario_id):
    errors = []
    if scenario_id == '':
        return json.dumps(['Scenario not found']), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps(['Scenario not found']), 404

    if g.user is None or (not g.user.is_admin() and scenario.owner != g.user):
        return json.dumps(['Scenario not found']), 404

    db.session.delete(scenario)
    db.session.commit()

    return json.dumps({
        'success': True
    }), 200


@mod.route('/clone_scenario/<scenario_id>', methods=['GET'])
@requires_login
def clone_scenario(scenario_id):
    errors = []
    if scenario_id == '':
        return json.dumps(['Scenario not found']), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps(['Scenario not found']), 404

    if not scenario.can_access(g.user):
        return json.dumps(['Scenario not found']), 404

    new_scenario = Scenario('Cloned of ' + scenario.name, g.user, addition_information=scenario.addition_information, is_public=1)

    db.session.add(new_scenario)
    db.session.commit()

    return json.dumps(new_scenario.to_dict(include_owner=True)), 200


@mod.route('/get_building_model')
def get_building_model():
    errors = []
    building_model_id = request.args.get('id', '')
    if building_model_id == '':
        return json.dumps(['Building model not found']), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps(['Building model not found']), 404

    return json.dumps(building_model.to_dict(include_owner=True, include_comments=True))


@mod.route('/view_building_model')
def view_building_model():
    building_model_id = request.args.get('id', '')
    if building_model_id == '':
        return render_template('404.html'), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return render_template('404.html'), 404

    '''if building_model.is_public == 0:
        if g.user is None:
            return render_template('404.html'), 404
        elif not (g.user.is_admin() or building_model.owner == g.user):
            return render_template('404.html'), 404'''

    return render_template("sketchup/view_building_model.html", building_model=building_model.to_dict(include_owner=True, include_comments=True))


@mod.route('/delete_building_model/<building_model_id>', methods=['GET'])
@requires_login
def delete_building_model(building_model_id):
    errors = []
    if building_model_id == '':
        return json.dumps(['Building model not found']), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps(['Building model not found']), 404

    if g.user is None or (not g.user.is_admin() and building_model.owner != g.user):
        return json.dumps(['Building model not found']), 404

    db.session.delete(building_model)
    db.session.commit()

    return json.dumps({
        'success': True
    }), 200


@mod.route('/update_building_model/<building_model_id>', methods=['POST'])
@requires_login
def update_building_model(building_model_id):
    errors = []
    if building_model_id == '':
        return json.dumps(['Building model not found']), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps(['Building model not found']), 404

    if not building_model.can_edit(g.user):
        return json.dumps(['Building model not found']), 404

    #only change name
    building_model_name = request.form.get('building_model_name', '')
    if building_model_name != '':
        building_model.name = building_model_name

    #change addition information
    addition_information = request.form.get('addition_information', '')
    if addition_information != '':
        try:
            addition_information = json.loads(addition_information)
            original_addition_information = json.loads(building_model.addition_information)
            for key in addition_information:
                original_addition_information[key] = addition_information[key]

            building_model.addition_information = json.dumps(original_addition_information)
        except:
            errors.append('Error in saving addition information, please contact an admin for more information')

    db.session.commit()

    return json.dumps({
        'success': True
    }), 200


@mod.route('/clone_building_model/<building_model_id>', methods=['GET'])
@requires_login
def clone_building_model(building_model_id):
    errors = []
    if building_model_id == '':
        return json.dumps(['Building model not found']), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps(['Building model not found']), 404

    new_building_model = BuildingModel('Clone of ' + building_model.name, building_model.data_file, g.user, addition_information=building_model.addition_information)
    new_building_model.file_type = building_model.file_type
    db.session.add(new_building_model)
    db.session.commit()

    return json.dumps(new_building_model.to_dict(include_owner=True)), 200


@mod.route('/base_scenarios', methods=['GET'])
def base_scenarios_page():
    return render_template("sketchup/base_scenarios.html")


@mod.route('/get_base_scenarios', methods=['POST'])
def get_base_scenarios():
    query = Scenario.query.filter(Scenario.is_base_scenario==1)
    filter_text = request.form.get('filter_text', '')
    if filter_text != '':
        query = query.filter(Scenario.name.like('%'+filter_text+'%'))
    if g.user is None or not g.user.is_admin():
        query = query.filter(Scenario.is_public==1)

    query = query.order_by(Scenario.created_time.desc())
    result = query.all()

    scenarios = []
    for scenario in result:
        scenarios.append(scenario.to_dict())

    return json.dumps({'scenarios': scenarios})