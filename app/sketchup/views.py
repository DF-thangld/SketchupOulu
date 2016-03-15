import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.uploads import UploadSet, IMAGES
from sqlalchemy.dialects import mysql

from app import db, send_mail, upload_file, save_image, delete_file
from app.users.decorators import requires_login
from app.users.models import User
from app.sketchup.models import Scenario, BuildingModel, Comment, CommentTopic
import app.utilities as utilities
from flask.ext.babel import gettext

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

    building_models = []
    if g.user is not None and scenario.can_edit(g.user):
        building_models = g.user.get_available_building_models(return_dict=True)

    return render_template("sketchup/view_scenario.html", can_edit=scenario.can_edit(g.user), building_models=building_models, scenario=scenario.to_dict(include_owner=True, include_last_edited_user=True, include_comments=True))


@mod.route('/edit_scenario/')
def edit_scenario():
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

    building_models = []
    if g.user is not None and scenario.can_edit(g.user):
        building_models = g.user.get_available_building_models(return_dict=True)

    return render_template("sketchup/edit_scenario.html", can_edit=scenario.can_edit(g.user), building_models=building_models, scenario=scenario.to_dict(include_owner=True, include_last_edited_user=True, include_comments=True))


@mod.route('/get_scenario/')
def get_scenario():
    errors = []
    scenario_id=request.args.get('id', '')
    if scenario_id == '':
        return json.dumps([gettext('Scenario not found')]), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps([gettext('Scenario not found')]), 404

    if scenario.is_public == 0 and not (scenario.owner == g.user or g.user.is_admin()):
        return json.dumps([gettext('Scenario not found')]), 404

    return json.dumps(scenario.to_dict(include_owner=True, include_last_edited_user=True, include_comments=True))


@mod.route('/update_scenario/<scenario_id>', methods=['POST'])
@requires_login
def update_scenario(scenario_id):
    errors = []
    if scenario_id == '':
        return json.dumps([gettext('Scenario not found')]), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps([gettext('Scenario not found')]), 404

    if not scenario.can_edit(g.user):
        return json.dumps([gettext('Scenario not found')]), 404

    if 'scenario_name' in request.form:
        scenario_name = request.form.get('scenario_name', '')
        if scenario_name == '':
            errors.append(gettext('Scenario name cannot be blank'))
        scenario.name = scenario_name

    if 'is_public' in request.form:
        is_public = request.form.get('is_public', 1)
        if is_public not in (1, 0):
            is_public = 1
        scenario.is_public = is_public

    if 'scenario_description' in request.form:
        description = request.form.get('scenario_description', '')
        scenario.description = description

    if 'addition_information' in request.form:
        addition_information = request.form.get('addition_information', '')
        try:
            json.loads(addition_information)
            scenario.addition_information = addition_information
        except:
            pass
        
    if 'scenario_preview' in request.form:
        scenario_preview = request.form.get('scenario_preview', '')
        if scenario_preview != '':
            try:
                save_image(scenario.id + '.png', 'static/images/scenario_previews', scenario_preview)
                scenario.has_preview = 1
            except:
                pass

    if len(errors) > 0:
        return json.dumps(errors), 400

    db.session.commit()
    return json.dumps({
        'success': True
    }), 200


@mod.route('/delete_scenario/<scenario_id>', methods=['GET'])
@requires_login
def delete_scenario(scenario_id):
    errors = []
    if scenario_id == '':
        return json.dumps([gettext('Scenario not found')]), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps([gettext('Scenario not found')]), 404

    if g.user is None or (not g.user.is_admin() and scenario.owner != g.user):
        return json.dumps([gettext('Scenario not found')]), 404
    
    db.session.delete(scenario)
    db.session.commit()
    delete_file('static/images/scenario_previews', scenario.id + '.png')

    return json.dumps({
        'success': True
    }), 200


@mod.route('/clone_scenario/<scenario_id>', methods=['GET'])
@requires_login
def clone_scenario(scenario_id):
    errors = []
    if scenario_id == '':
        return json.dumps([gettext('Scenario not found')]), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps([gettext('Scenario not found')]), 404

    if not scenario.can_access(g.user):
        return json.dumps([gettext('Scenario not found')]), 404

    new_scenario = Scenario(gettext('Cloned of %(scenario_name)s', scenario_name=scenario.name), g.user, addition_information=scenario.addition_information, is_public=1)

    db.session.add(new_scenario)
    db.session.commit()

    return json.dumps(new_scenario.to_dict(include_owner=True)), 200


@mod.route('/get_building_model')
def get_building_model():
    errors = []
    building_model_id = request.args.get('id', '')
    if building_model_id == '':
        return json.dumps([gettext('Building model not found')]), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps([gettext('Building model not found')]), 404

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
        return json.dumps([gettext('Building model not found')]), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps([gettext('Building model not found')]), 404
    if building_model.is_base_item == 1:
        return json.dumps([gettext('Cannot delete base item')]), 400

    if g.user is None or (not g.user.is_admin() and building_model.owner != g.user):
        return json.dumps([gettext('Building model not found')]), 404

    db.session.delete(building_model.comment_topic)
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
        return json.dumps([gettext('Building model not found')]), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps([gettext('Building model not found')]), 404

    if not building_model.can_edit(g.user):
        return json.dumps([gettext('Building model not found')]), 404

    #only change name
    if 'building_model_name' in request.form:
        building_model_name = request.form.get('building_model_name', '')
        if building_model_name != '':
            building_model.name = building_model_name
        else:
            return json.dumps([gettext('Model name is required')]), 400

    #change building status to building item
    if g.user.is_admin():
        if 'is_base_item' in request.form:
            if building_model.is_base_item == 0:
                building_model.is_base_item = 1
            else:
                building_model.is_base_item = 0

    #change addition information
    if 'addition_information' in request.form:
        addition_information = request.form.get('addition_information', '')
        if addition_information != '':
            try:
                addition_information = json.loads(addition_information)
                original_addition_information = json.loads(building_model.addition_information)
                for key in addition_information:
                    original_addition_information[key] = addition_information[key]

                building_model.addition_information = json.dumps(original_addition_information)
            except:
                return json.dumps([gettext('Error in saving addition information, please contact an admin for more information')]), 400
    
    if 'preview' in request.form:
        preview = request.form.get('preview', '')
        if preview != '':
            try:
                save_image(building_model.id + '.png', 'static/images/building_model_previews', preview)
                building_model.has_preview = 1
            except:
                pass
        

    db.session.commit()
    returned_building_model = {}
    if g.user.is_admin():
        returned_building_model = {'id': building_model.id, 'name': building_model.name, 'addition_information': building_model.addition_information, 'is_base_item': building_model.is_base_item}
    else:
        returned_building_model = {'id': building_model.id, 'name': building_model.name, 'addition_information': building_model.addition_information}

    return json.dumps({
        'success': True,
        'building_model': returned_building_model
    }), 200


@mod.route('/clone_building_model/<building_model_id>', methods=['GET'])
@requires_login
def clone_building_model(building_model_id):
    errors = []
    if building_model_id == '':
        return json.dumps([gettext('Building model not found')]), 404

    building_model = BuildingModel.query.filter_by(id=building_model_id).first()
    if building_model is None:
        return json.dumps([gettext('Building model not found')]), 404

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

@mod.route('/get_predefined_building_models', methods=['GET', 'POST'])
def get_predefined_building_models():
    query = BuildingModel.query.filter(BuildingModel.is_base_item==1)

    query = query.order_by(BuildingModel.created_time.desc())
    result = query.all()

    building_models = []
    for building_model in result:
        building_models.append(building_model.to_dict())

    return json.dumps(building_models)