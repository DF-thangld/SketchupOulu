import json
import datetime
import zipfile
import os
import shutil
import re


from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, make_response, render_template_string
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.babel import gettext

from app import db, send_mail, upload_file, app_dir, save_image
from app.users.forms import RegisterForm, LoginForm, UserProfileForm, ResetPasswordForm
from app.users.models import User, UserSession, Group
from app.sketchup.models import Scenario, BuildingModel, CommentTopic, Comment
from app.users.decorators import requires_login
from app.journal.models import Journal
import app.utilities as utilities
import config

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

@mod.route('/resend_activation_email/<code>', methods=['GET'])
def resend_activation_email(code):
    if code.strip() == '':
        return render_template("404.html"), 404
    user = User.query.filter(User.verification_code==code).first()
    if user is None:
        return render_template("404.html"), 404
    
    email_activation = Journal.query.filter(Journal.id==120).first().get_journal_content(session['locale'])
    send_mail([user.email], email_activation.title, render_template_string(email_activation.content, activate_link=url_for('users.verify_account', code=code, _external=True)))
    
    return render_template("users/register_finish.html", email=user.email)
    
    
@mod.route('/verify_account/<code>', methods=['GET'])
def verify_account(code):
    if code.strip() == '':
        return render_template("404.html"), 404
    user = User.query.filter(User.verification_code==code).first()
    if user is None:
        return render_template("404.html"), 404
    session['user_id'] = user.id
    g.user = user
    user.banned = 0
    user.verification_code = ''

    #add remember
    user_session = UserSession(user.id)
    db.session.add(user_session)
    db.session.commit()
    response = make_response(render_template('users/verify_account.html'))
    cookie_value = str(user.id) + '|' + user_session.token
    response.set_cookie('session_id', cookie_value, expires=datetime.datetime.now() + datetime.timedelta(days=5), path='/')
    return response
    

@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login form
    """
    form = LoginForm(request.form)
    errors = []
    # make sure data are valid, but doesn't validate password is right
    if form.is_submitted():
        is_validated = True
        #validate email
        if form.email.data.strip() == '':
            is_validated = False
            errors.append(gettext('Email is required'))
        #validate valid email
        match = re.search(r'^.+@([^.@][^@]+)$', form.email.data.strip())
        if not match:
            is_validated = False
            errors.append(gettext('Invalid email address'))
        
        if form.password.data.strip() == '':
            is_validated = False
            errors.append(gettext('Password field is required'))
            
        if is_validated:
            user = User.query.filter_by(email=form.email.data.lower()).first()  # @UndefinedVariable

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
            elif user and check_password_hash(user.password, form.password.data) and user.banned == 2:
                errors.append(gettext('The account is not activated, please check your email for verification. <a href="%(resend_activation_email)s">Resend activation email</a>', resend_activation_email=url_for('users.resend_activation_email', code=user.verification_code)))
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
        is_validated = True
        if form.name.data.strip() == '':
            is_validated = False
            errors.append(gettext('Username is required'))
        #validate email
        if form.email.data.strip() == '':
            is_validated = False
            errors.append(gettext('Email is required'))
        #validate valid email
        match = re.search(r'^.+@([^.@][^@]+)$', form.email.data.strip())
        if not match:
            is_validated = False
            errors.append(gettext('Invalid email address'))
        
        if form.password.data.strip() == '':
            is_validated = False
            errors.append(gettext('Password field is required'))
            
        if form.confirm.data.strip() == '':
            is_validated = False
            errors.append(gettext('You have to confirm your password'))
        if form.confirm.data != form.password.data:
            is_validated = False
            errors.append(gettext('Passwords must match'))
        
        if len(form.recaptcha.errors) > 0:
            is_validated = False
            errors.append(gettext('Captcha was incorrect'))
            
        if is_validated:
            same_username_user = User.query.filter_by(username=form.name.data).first()
            same_email_user = User.query.filter_by(email=form.email.data).first()
            if same_email_user is not None:
                errors.append(gettext('Duplicate email address'))
            if same_username_user is not None:
                errors.append(gettext('Duplicate username'))

            if len(errors) > 0:
                return render_template("users/register.html", form=form, errors=errors)

            # Insert the record in our database and commit it
            user = User(username=form.name.data.lower(), email=form.email.data,
                        password=generate_password_hash(form.password.data))
            user.verification_code = utilities.generate_random_string(50)
            user.banned = 2
            db.session.add(user)
            db.session.commit()
            
            # send confirm email and redirect to confirm page
            email_activation = Journal.query.filter(Journal.id==120).first().get_journal_content(session['locale'])
            send_mail([user.email], email_activation.title, render_template_string(email_activation.content, activate_link=url_for('users.verify_account', code=user.verification_code, _external=True)))
            return render_template("users/register_finish.html", email=user.email)
        else:
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
            
            email_content = Journal.query.filter(Journal.id==122).first().get_journal_content(session['locale'])
            send_mail([user.email], email_content.title, render_template_string(email_content.content, new_password=new_password))
            return render_template("users/reset_password_confirmed.html"), 200


    form = ResetPasswordForm(request.form)
    errors = []
    # make sure data are valid, but doesn't validate password is right
    if form.is_submitted():
        is_validated = True
        if form.email.data.strip() == '':
            is_validated = False
            errors.append(gettext('Email is required'))
        #validate valid email
        match = re.search(r'^.+@([^.@][^@]+)$', form.email.data.strip())
        if not match:
            is_validated = False
            errors.append(gettext('Invalid email address'))
            
        if is_validated:
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
            email_content = Journal.query.filter(Journal.id==121).first().get_journal_content(session['locale'])
            send_mail([user.email], email_content.title, render_template_string(email_content.content, link=url_for('users.reset_password', token=user.password_token, _external=True)))
            db.session.commit()
            return render_template("users/reset_password_submited.html"), 200
        else:
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
        return json.dumps([gettext('Comment topic not found')]), 404
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
        return json.dumps([gettext('Comment topic not found')]), 404

    comments = main_object.comment_topic.get_latest_comments(page=page, return_dict=True)
    for comment in comments:
        if g.user is not None and (g.user.is_admin() or g.user.username == comment['owner']['username']):
            comment['can_edit'] = True
        else:
            comment['can_edit'] = False
        comment['content'] = comment['content'].replace('\n', '<br />')

    return json.dumps({'comments': comments,
                       'total_page': main_object.comment_topic.total_page,
                       'current_page': main_object.comment_topic.current_page,
                       'can_add_comment': can_add_comment})


@mod.route('/suggest_scenario/<scenario_id>', methods=['POST'])
@requires_login
def suggest_scenario(scenario_id):
    errors = []
    content = request.form.get('content', '')
    if content == '':
        errors.append(gettext('Suggest content is required'))
        return json.dumps(errors), 400
    
    scenario = Scenario.query.get(scenario_id)
    if scenario is None:
        errors.append('Scenario not found')
        return json.dumps(errors), 404
    comment_topic = scenario.comment_topic
    
    new_comment = Comment(g.user, comment_topic, content)
    new_comment.description = gettext('Suggest for scenario')
    db.session.add(new_comment)
    db.session.commit()

    #send email to admins about the suggested content
    admin_group = Group.query.get(1)
    admins = admin_group.users
    admin_emails = []
    for admin in admins:
        admin_emails.append(admin.email)
    send_mail(admin_emails, '[SketchupOulu] New suggest for ' + scenario.name, render_template("users/suggest_scenario_email_content.html", suggest_content=content, scenario=scenario.to_dict(), user=g.user.username))
    return json.dumps(new_comment.to_dict(include_owner=True)), 200


@mod.route('/add_comment/', methods=['POST'])
@requires_login
def add_comment():
    errors = []
    comment_type = request.form.get('comment_type', '')
    object_id = request.form.get('object_id', '')
    content = request.form.get('content', '')
    if content == '':
        errors.append(gettext('Comment content is required'))
        return json.dumps(errors), 400
    if object_id == '':
        errors.append(gettext('Comment object is required'))
        return json.dumps(errors), 400

    comment_topic = None
    if comment_type == 'scenario':
        scenario = Scenario.query.get(object_id)
        if scenario is None:
            errors.append('Scenario not found')
            return json.dumps(errors), 404
        if not scenario.can_access(g.user):
            errors.append(gettext('You don\'t have permission to add comment here'))
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
        errors.append(gettext('Comment type not found'))
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
        errors.append(gettext('Comment not found'))
        return json.dumps(errors), 404

    comment = Comment.query.get(comment_id)
    if comment is None:
        errors.append(gettext('Comment not found'))
        return json.dumps(errors), 404

    if comment.owner == g.user or g.user.is_admin() or comment.topic.owner == g.user:
        db.session.delete(comment)
        db.session.commit()
        return json.dumps({'success': True, 'comment_id': comment_id}), 200
    else:
        errors.append(gettext('Unauthorized deletion'))
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
        scenario_preview = request.form.get('scenario_preview', '')
        if name.strip() == '':
            errors.append('Scenario name is required')
            return render_template("users/add_scenario.html", errors=errors, building_models=building_models), 400

        scenario = Scenario(name, g.user, addition_information=addition_information, is_public=is_public)
        scenario.description = request.form.get('description', '')
        
        # save preview to dir
        save_image(scenario.id + '.png', 'static/images/scenario_previews', scenario_preview)
        scenario.has_preview = 1
        
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

        if name.strip() == '':
            errors.append(gettext('Scenario name is required'))
        if request.files['data_file'].filename == '':
            errors.append(gettext('Model file is required'))
        if len(errors) > 0:
            return render_template("users/add_building_model.html", errors=errors), 400

        uploaded_file = upload_file(request.files['data_file'], 'static/models/building_models', file_type="model")
        data_file = uploaded_file['filename']
        if uploaded_file['extension'] not in config.ALLOWED_FILE_TYPES:
            errors.append('Unrecognized model file format')
            try:
                os.remove(os.path.join(app_dir, 'static/models/building_models', data_file))
            except:
                pass
            return render_template("users/add_building_model.html", errors=errors), 400
        if os.stat(os.path.join(app_dir, 'static/models/building_models', data_file)).st_size >= 1024*1024*10:
            errors.append('File too big, max file size is 10MB')
            os.remove(os.path.join(app_dir, 'static/models/building_models', data_file))
            return render_template("users/add_building_model.html", errors=errors), 400
        #check if file type is zip => unzip it
        if uploaded_file['extension'] == 'zip':

            tmp = data_file

            zip_ref = zipfile.ZipFile(os.path.join(app_dir, 'static/models/building_models', data_file), 'r')
            zip_ref.extractall(os.path.join(app_dir, 'static/models/building_models', uploaded_file['filename_without_extension']))
            zip_ref.close()
            #os.rename(os.path.join(app_dir, 'static/models/building_models', uploaded_file['original_filename']), os.path.join(app_dir, 'static/models/building_models', uploaded_file['filename_without_extension']))
            zipped_dir = os.path.join(app_dir, 'static/models/building_models', uploaded_file['filename_without_extension'])

            #check if inside of the zip is a dir of contain file, if contain only 1 dir => move file from inside that dir outside
            tmp_files = os.listdir(zipped_dir)
            if len(tmp_files) == 1 and not os.path.isfile(os.path.join(zipped_dir, tmp_files[0])): #contain only 1 dir
                inside_files = os.listdir(os.path.join(zipped_dir, tmp_files[0]))
                new_name = utilities.generate_random_string(50)
                os.rename(os.path.join(zipped_dir, tmp_files[0]), os.path.join(zipped_dir, new_name))
                for file in inside_files:
                    try:
                        shutil.move(os.path.join(zipped_dir, new_name, file), os.path.join(zipped_dir, file))
                    except:
                        pass
                try:
                    shutil.rmtree(os.path.join(zipped_dir, new_name)) #delete unzipped folder
                except:
                    pass


            files = [f for f in os.listdir(zipped_dir) if os.path.isfile(os.path.join(zipped_dir, f))]
            important_file_index = -1
            important_file_name = ''
            file_index = -1
            for file in files:
                filename_parts = file.split('.')
                current_filename = filename_parts[0]
                for i in range(1, len(filename_parts)-1):
                    current_filename += '.' + filename_parts[i]
                extension = filename_parts[len(filename_parts)-1].lower()
                os.rename(os.path.join(zipped_dir, file), os.path.join(zipped_dir, current_filename+'.'+extension))
                if important_file_index < 0:
                    file_index += 1
                    if extension in ['dae', 'obj']:
                        important_file_name = current_filename
                        important_file_index = file_index
                        file_type = extension

            if important_file_index < 0: # user uploaded unrecognized file
                errors.append(gettext('Unrecognized model file format'))
                os.remove(os.path.join(app_dir, 'static/models/building_models', data_file))
                try:
                    shutil.rmtree(os.path.join(app_dir, 'static/models/building_models', uploaded_file['filename_without_extension'])) #delete unzipped folder
                except:
                    pass
                return render_template("users/add_building_model.html", errors=errors), 400
            if file_type == 'obj': # important file is obj inside a zipped => objmtl
                file_type = 'objmtl'

            addition_information = {'original_filename': important_file_name,
                                    'directory': uploaded_file['filename_without_extension'],
                                    'camera_x': 30, 'camera_y': 250, 'camera_z': 350,
                                    "camera_lookat_x": 31, "camera_lookat_y": 222, "camera_lookat_z": 366}
        else:
            file_type = uploaded_file['extension']
            addition_information = {'original_filename': uploaded_file['filename_without_extension'],
                                    'directory': '',
                                    'camera_x': 30, 'camera_y': 250, 'camera_z': 350,
                                    "camera_lookat_x": 31, "camera_lookat_y": 222, "camera_lookat_z": 366}
                

        building_model = BuildingModel(name, data_file, g.user, addition_information=addition_information)
        building_model.file_type = file_type
        building_model.addition_information = json.dumps(addition_information, ensure_ascii=False)
        db.session.add(building_model)
        db.session.commit()
        return redirect(url_for('sketchup.view_building_model', id=building_model.id))


