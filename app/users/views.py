import json
import datetime
import zipfile
import os

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, make_response
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.babel import gettext

from app import db, send_mail, upload_file, app_dir
from app.users.forms import RegisterForm, LoginForm, UserProfileForm, ResetPasswordForm
from app.users.models import User, UserSession
from app.sketchup.models import Scenario, BuildingModel, CommentTopic, Comment
from app.users.decorators import requires_login
import app.utilities as utilities

mod = Blueprint('users', __name__, url_prefix='/users')


@mod.route('/<username>/profile/')
def profile(username):

    user = User.query.filter_by(username=username).first()
    if user is None:
        return render_template('404.html')

    scenarios = user.get_scenarios(return_dict=True)
    building_models = user.get_available_building_models(include_base_models=False,return_dict=True)
    comments = user.get_comments()
    return render_template("users/profile.html", user=user, scenarios=scenarios, building_models=building_models, comments=comments)


@mod.route('/profile/')
@requires_login
def own_profile():
    return profile(g.user.username)


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login form
    """
    form = LoginForm(request.form)
    errors = []
    # make sure data are valid, but doesn't validate password is right
    if form.is_submitted():
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()  # @UndefinedVariable

            
            # we use werzeug to validate user's password
            if user is None:
                errors.append(gettext('Wrong email or password'))
                return render_template("users/login.html", form=form, errors=errors)
            elif user and not check_password_hash(user.password, form.password.data):
                user.last_login_attempt = datetime.datetime.now()
                user.login_attempts += 1
                db.session.commit()
                errors.append(gettext('Wrong email or password'))
                return render_template("users/login.html", form=form, errors=errors)
            elif user and check_password_hash(user.password, form.password.data) and user.banned == 1:
                errors.append(gettext('The account was banned, please contact an admin for more information'))
                return render_template("users/login.html", form=form, errors=errors)
            elif user and check_password_hash(user.password, form.password.data):
                # the session can't be modified as it's signed,
                # it's a safe place to store the user id
                session['user_id'] = user.id

                user.last_login = datetime.datetime.now()
                user.last_login_attempt = None
                user.login_attempts = 0
                g.user = user

                user_session = UserSession(user.id)
                db.session.add(user_session)
                db.session.commit()
                response = make_response(redirect(url_for('users.own_profile')))
                cookie_value = str(user.id) + '|' + user_session.token
                response.set_cookie('session_id', cookie_value, expires=datetime.datetime.now() + datetime.timedelta(days=5), path='/')
                return response
        else:
            for error in form.email.errors:
                errors.append(error)
            for error in form.password.errors:
                errors.append(error)
            return render_template("users/login.html", form=form, errors=errors)

    return render_template("users/login.html", form=form, errors=[])

@mod.route('/register/', methods=['GET', 'POST'])
def register():
    """
    Registration Form
    """
    
    form = RegisterForm(request.form)
    errors = []

    if form.is_submitted():
        if form.validate():
            same_username_user = User.query.filter_by(username=form.name.data).first()
            same_email_user = User.query.filter_by(email=form.email.data).first()
            if same_email_user is not None:
                errors.append(gettext('Duplicate email address'))
            if same_username_user is not None:
                errors.append(gettext('Duplicate username'))

            if len(errors) > 0:
                return render_template("users/register.html", form=form, errors=errors)

            # Insert the record in our database and commit it
            user = User(username=form.name.data, email=form.email.data,
                        password=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            # TODO: send confirm email and redirect to confirm page

            # Log the user in, as he now has an id
            session['user_id'] = user.id
            g.user = user

            #add remember
            user_session = UserSession(user.id)
            db.session.add(user_session)
            db.session.commit()
            response = make_response(redirect(url_for('users.own_profile')))
            cookie_value = str(user.id) + '|' + user_session.token
            response.set_cookie('session_id', cookie_value, expires=datetime.datetime.now() + datetime.timedelta(days=5), path='/')
            return response

        else:
            for error in form.name.errors:
                errors.append(error)
            for error in form.email.errors:
                errors.append(error)
            for error in form.password.errors:
                errors.append(error)
            for error in form.confirm.errors:
                errors.append(error)
            for error in form.recaptcha.errors:
                errors.append(error)
            return render_template("users/register.html", form=form, errors=errors)
    return render_template("users/register.html", form=form, errors=[])

@mod.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():

    token = request.args.get('token', '')
    if token != '':
        user = User.query.filter_by(password_token=token).first()
        if user is not None:

            new_password = utilities.generate_random_string(20)
            user.password = generate_password_hash(new_password)
            user.password_token = ''
            db.session.commit()

            email_content = gettext('Finally, support has come to help you :)<br /><br />')
            email_content += gettext('Your new password: <b>%(new_password)s</b><br /><br />', new_password=new_password)
            email_content += gettext('Thanks,<br />')
            email_content += gettext('Sketchup Oulu team')
	
            send_mail([user.email], gettext('[SketchupOulu] Your new password'), email_content)
            return render_template("users/reset_password_confirmed.html"), 200


    form = ResetPasswordForm(request.form)
    errors = []
    # make sure data are valid, but doesn't validate password is right
    if form.is_submitted():
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()  # @UndefinedVariable

            if user is None:
                errors.append(gettext('Account not found'))
                return render_template("users/reset_password.html", form=form, errors=errors), 404

            if user.banned == 1:
                errors.append(gettext('The account was banned, please contact an admin for more information'))
                return render_template("users/reset_password.html", form=form, errors=errors), 400

            user.password_token = utilities.generate_random_string(50)
            db.session.commit()

            # we use werzeug to validate user's password
            email_content = 'We heard that you lost your password. Sorry about that!<br /><br />'
            email_content += 'But don\'t worry! You can use the following link to reset your password:<br /><br />'
            email_content += '<a href="' + url_for('users.reset_password', token=user.password_token, _external=True) + '">' + url_for('users.reset_password', token=user.password_token, _external=True) + '</a><br /><br />'
            #email_content += 'If you don\'t use this link within 24 hours, it will expire. To get a new password reset link, visit ' + url_for('users.reset_password') + ' \n\n'
            email_content += 'Thanks,<br />'
            email_content += 'Sketchup Oulu team'

            send_mail([user.email], '[SketchupOulu] Reset your password', email_content)
            user.password_token = ''
            db.session.commit()
            return render_template("users/reset_password_submited.html"), 200
        else:
            for error in form.email.errors:
                errors.append(error)
            return render_template("users/reset_password.html", form=form, errors=errors), 200

    return render_template("users/reset_password.html", form=form, errors=[])

@mod.route('/change_password/', methods=['GET', 'POST'])
@requires_login
def change_password():
    errors = []
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if old_password == '':
        errors.append('Old password is required')
    if new_password == '':
        errors.append('New password is required')
    if confirm_password == '':
        errors.append('You have to confirm your password')
    if new_password != '' and new_password != confirm_password:
        errors.append('Password must match')
    if len(errors) > 0:
        return json.dumps(errors), 400

    if not check_password_hash(g.user.password, old_password):
        errors.append('Wrong old password')
    if len(errors) > 0:
        return json.dumps(errors), 400

    user = User.query.get(g.user.id)
    user.password = generate_password_hash(new_password)
    user.password_token = ''
    db.session.commit()
    g.user = user
    return json.dumps({'success': True}), 200

@mod.route('/logout/', methods=['GET'])
@requires_login
def logout():
    session.clear()
    session['user_id'] = None
    g.user = None
    response = make_response(redirect(url_for('index')))
    response.set_cookie('session_id', '', expires=0, path='/')
    return response

@mod.route('/user_profile/', methods=['GET', 'POST'])
@requires_login
def user_profile():
    form = UserProfileForm()
    if form.is_submitted():
        user = User.query.filter_by(id=session.get('user_id')).first()
        user.fullname = form.fullname.data
        user.address = form.address.data
        user.phone_number = form.phone_number.data

        db.session.commit()

        g.user = user

    form.email.data = g.user.email
    form.username.data = g.user.username
    form.fullname.data = g.user.fullname
    form.address.data = g.user.address
    form.phone_number.data = g.user.phone_number
    #form.birthdate.data = g.user.birthdate

    return render_template("users/user_profile.html", form=form)


@mod.route('/upload_profile_picture/', methods=['POST'])
@requires_login
def upload_profile_picture():

    user = User.query.get(g.user.id)
    user.profile_picture = upload_file(request.files['profile_picture'], 'static/images/profile_pictures')['filename']
    g.user = user
    db.session.commit()

    return url_for('static', filename='images/profile_pictures/' + user.profile_picture, _external=True)


@mod.route('/get_comments/')
def get_comments():
    comment_type = request.args.get('comment_type', '')
    comment_id = request.args.get('comment_id', '')
    page = request.args.get('page', '1')

    if comment_id == '' or comment_type not in ['user', 'scenario', 'building_model']:
        return json.dumps(['Comment topic not found']), 404
    if page.isdigit():
        page = int(page)
        if page < 1:
            page = 1
    else:
        page = 1

    can_add_comment = False

    main_object = None
    if comment_type == 'user':
        main_object = User.query.filter_by(id=comment_id).first()
        can_add_comment = True
    elif comment_type == 'scenario':
        main_object = Scenario.query.filter_by(id=comment_id).first()
        if main_object.can_access(g.user):
            can_add_comment = True
    elif comment_type == 'building_model':
        main_object = BuildingModel.query.filter_by(id=comment_id).first()
        can_add_comment = True
    if main_object is None:
        return json.dumps(['Comment topic not found']), 404

    comments = main_object.comment_topic.get_latest_comments(page=page, return_dict=True)
    for comment in comments:
        if g.user is not None and (g.user.is_admin() or g.user.username == comment['owner']['username']):
            comment['can_edit'] = True
        else:
            comment['can_edit'] = False

    return json.dumps({'comments': comments,
                       'total_page': main_object.comment_topic.total_page,
                       'current_page': main_object.comment_topic.current_page,
                       'can_add_comment': can_add_comment})


@mod.route('/add_comment/', methods=['POST'])
@requires_login
def add_comment():
    errors = []
    comment_type = request.form.get('comment_type', '')
    object_id = request.form.get('object_id', '')
    content = request.form.get('content', '')
    if content == '':
        errors.append('Comment content is required')
        return json.dumps(errors), 400
    if object_id == '':
        errors.append('Comment object is required')
        return json.dumps(errors), 400

    comment_topic = None
    if comment_type == 'scenario':
        scenario = Scenario.query.get(object_id)
        if scenario is None:
            errors.append('Scenario not found')
            return json.dumps(errors), 404
        if not scenario.can_access(g.user):
            errors.append('You don\'t have permission to add comment here')
            return json.dumps(errors), 401
        comment_topic = scenario.comment_topic
    elif comment_type == 'building_model':
        building_model = BuildingModel.query.get(object_id)
        if building_model is None:
            errors.append('Building model not found')
            return json.dumps(errors), 404
        comment_topic = building_model.comment_topic
    elif comment_type == 'user':
        user = User.query.get(object_id)
        if user is None:
            errors.append('User not found')
            return json.dumps(errors), 404
        comment_topic = user.comment_topic
    else:
        errors.append('Comment type not found')
        return json.dumps(errors), 401

    new_comment = Comment(g.user, comment_topic, content)
    db.session.add(new_comment)
    db.session.commit()

    return json.dumps(new_comment.to_dict(include_owner=True)), 200

@mod.route('/delete_comment/', methods=['POST'])
@requires_login
def delete_comment():
    errors = []
    comment_id = request.form.get('comment_id', 0)
    if comment_id == 0:
        errors.append('Comment not found')
        return json.dumps(errors), 404

    comment = Comment.query.get(comment_id)
    if comment is None:
        errors.append('Comment not found')
        return json.dumps(errors), 404

    if comment.owner == g.user or g.user.is_admin() or comment.topic.owner == g.user:
        db.session.delete(comment)
        db.session.commit()
        return json.dumps({'success': True, 'comment_id': comment_id}), 200
    else:
        errors.append('Unauthorized deletion')
        return json.dumps(errors), 403


@mod.route('/<username>/scenarios/', methods=['GET', 'POST'])
def user_scenarios_page(username):
    if username == '':
        return render_template("404.html"), 404
    user = User.query.filter(User.username==username).first()
    if user is None:
        return render_template("404.html"), 404

    return render_template("users/scenarios.html", user=user.to_dict())


@mod.route('/scenarios/', methods=['GET', 'POST'])
@requires_login
def user_own_scenarios_page():
    return user_scenarios_page(g.user.username)


@mod.route('/<username>/get_user_scenarios/', methods=['POST'])
def get_user_scenarios(username):
    if username == '':
        return render_template("404.html"), 404
    user = User.query.filter(User.username==username).first()
    if user is None:
        return render_template("404.html"), 404

    filter_text = request.form.get('filter_text', '')
    page = request.form.get('page', '1')
    if page.isdigit():
        page = int(page)
        if page < 1:
            page = 1
    else:
        page = 1

    scenarios = user.get_scenarios(filter_text, page, True, g.user)
    return json.dumps({'scenarios': scenarios,
                       'total_page': user.scenarios_total_page,
                       'current_page': user.scenarios_current_page})


@mod.route('/get_user_scenarios/', methods=['POST'])
@requires_login
def user_own_scenarios():
    return get_user_scenarios(g.user.username)


@mod.route('/add_scenario/', methods=['GET','POST'])
@requires_login
def add_scenario():
    errors = []
    building_models = g.user.get_available_building_models(return_dict=True)
    if request.method == 'GET':
        return render_template("users/add_scenario.html", errors=errors, building_models=building_models)
    else:
        name = request.form.get('name', '')
        is_public = request.form.get('is_public', 0)
        addition_information = request.form.get('addition_information', '')
        if name.strip() == '':
            errors.append('Scenario name is required')
            return render_template("users/add_scenario.html", errors=errors, building_models=building_models), 400

        scenario = Scenario(name, g.user, addition_information=addition_information, is_public=is_public)
        scenario.description = request.form.get('description', '')
        db.session.add(scenario)
        db.session.commit()
        return redirect(url_for('sketchup.view_scenario', id=scenario.id))


@mod.route('/<username>/building_models/', methods=['GET', 'POST'])
def user_building_models_page(username):
    if username == '':
        return render_template("404.html"), 404
    user = User.query.filter(User.username==username).first()
    if user is None:
        return render_template("404.html"), 404

    return render_template("users/building_models.html", user=user.to_dict())


@mod.route('/building_models/', methods=['GET', 'POST'])
@requires_login
def user_own_building_models_page():
    return user_building_models_page(g.user.username)


@mod.route('/<username>/get_user_building_models/', methods=['POST'])
def get_user_building_models(username):
    if username == '':
        return render_template("404.html"), 404
    user = User.query.filter(User.username==username).first()
    if user is None:
        return render_template("404.html"), 404

    filter_text = request.form.get('filter_text', '')
    page = request.form.get('page', '1')
    if page.isdigit():
        page = int(page)
        if page < 1:
            page = 1
    else:
        page = 1

    if filter_text != '':
        query = BuildingModel.query.filter(BuildingModel.owner==user)\
            .filter(BuildingModel.name.like('%'+filter_text+'%'))
    else:
        query = BuildingModel.query.filter(BuildingModel.owner==user)\

    query = query.order_by(BuildingModel.created_time.desc())

    page_data = query.paginate(page, 20, False)
    building_models_total_page = page_data.pages
    building_models_current_page = page

    building_models = []
    for building_model in page_data.items:
        building_models.append(building_model.to_dict())

    return json.dumps({'building_models': building_models,
                       'total_page': building_models_total_page,
                       'current_page': building_models_current_page})


@mod.route('/get_user_building_models/', methods=['POST'])
@requires_login
def user_own_building_models():
    return get_user_building_models(g.user.username)


@mod.route('/add_building_model/', methods=['GET', 'POST'])
@requires_login
def add_building_model():
    errors = []
    if request.method == 'GET':
        return render_template("users/add_building_model.html", errors=errors)
    else:
        addition_information = ''
        name = request.form.get('name', '')
        file_type = request.form.get('file_type', '')

        if name.strip() == '':
            errors.append('Scenario name is required')
        if file_type.strip() == '':
            errors.append('File type is required')
        if request.files['data_file'].filename == '':
            errors.append('Model file is required')
        if len(errors) > 0:
            return render_template("users/add_building_model.html", errors=errors), 400

        uploaded_file = upload_file(request.files['data_file'], 'static/models/building_models', file_type="model")
        data_file = uploaded_file['filename']
        #check if file type is zip => unzip it
        if uploaded_file['extension'] == 'zip':
            zip_ref = zipfile.ZipFile(os.path.join(app_dir, 'static/models/building_models', data_file), 'r')
            zip_ref.extractall(os.path.join(app_dir, 'static/models/building_models'))
            zip_ref.close()
            os.rename(os.path.join(app_dir, 'static/models/building_models', uploaded_file['original_filename']), os.path.join(app_dir, 'static/models/building_models', uploaded_file['filename_without_extension']))
            #TODO: searching the unzipped files for fail-safe human errors with file type
            addition_information = {'original_filename': uploaded_file['original_filename'],
                                    'directory': uploaded_file['filename_without_extension'],
                                    'camera_x': 30, 'camera_y': 250, 'camera_z': 350,
                                    "camera_lookat_x": 31, "camera_lookat_y": 222, "camera_lookat_z": 366}
        else:
            addition_information = {'original_filename': uploaded_file['filename_without_extension'],
                                    'directory': '',
                                    'camera_x': 30, 'camera_y': 250, 'camera_z': 350,
                                    "camera_lookat_x": 31, "camera_lookat_y": 222, "camera_lookat_z": 366}


        building_model = BuildingModel(name, data_file, g.user, addition_information=addition_information)
        building_model.file_type = file_type
        building_model.addition_information = json.dumps(addition_information)
        db.session.add(building_model)
        db.session.commit()
        return redirect(url_for('sketchup.view_building_model', id=building_model.id))


