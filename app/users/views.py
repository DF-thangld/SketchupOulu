import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.uploads import UploadSet, IMAGES

from app import db, send_mail, upload_picture
from app.users.forms import RegisterForm, LoginForm, UserProfileForm, ResetPasswordForm
from app.users.models import User
from app.users.decorators import requires_login
import app.utilities as utilities

mod = Blueprint('users', __name__, url_prefix='/users')

@mod.route('/profile/')
@requires_login
def profile():
    return render_template("users/profile.html", user=g.user)

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

            if user.banned == 1:
                errors.append('The account was banned, please contact an admin for more information')
                return render_template("users/login.html", form=form, errors=errors)
            # we use werzeug to validate user's password
            if user and check_password_hash(user.password, form.password.data):
                # the session can't be modified as it's signed,
                # it's a safe place to store the user id
                session['user_id'] = user.id
                g.user = user
                flash('Welcome %s' % user.username)
                return redirect(url_for('users.profile'))
            else:
                errors.append('Login fail, wrong email or password')
                return render_template("users/login.html", form=form, errors=errors)
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
                errors.append('Duplicate email address')
            if same_username_user is not None:
                errors.append('Duplicate username address')

            if len(errors) > 0:
                return render_template("users/register.html", form=form, errors=errors)

            # Insert the record in our database and commit it
            user = User(username=form.name.data, email=form.email.data,
                        password=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()

            # Log the user in, as he now has an id
            session['user_id'] = user.id
            g.user = user

            # flash will display a message to the user
            flash('Thanks for registering')
            # redirect user to the 'home' method of the user module.
            # TODO: send confirm email and redirect to confirm page
            return redirect(url_for('index'))
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

            email_content = 'Finally, support has come to help you :)<br /><br />'
            email_content += 'Your new password: <b>' + new_password + '</b><br /><br />'
            email_content += 'Thanks,<br />'
            email_content += 'Sketchup Oulu team'

            send_mail([user.email], '[SketchupOulu] Your new password‏', email_content)
            return render_template("users/reset_password_confirmed.html"), 200

    form = ResetPasswordForm(request.form)
    errors = []
    # make sure data are valid, but doesn't validate password is right
    if form.is_submitted():
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()  # @UndefinedVariable

            if user is None:
                errors.append('Account not found')
                return render_template("users/reset_password.html", form=form, errors=errors), 404

            if user.banned == 1:
                errors.append('The account was banned, please contact an admin for more information')
                return render_template("users/reset_password.html", form=form, errors=errors), 400

            user.password_token = utilities.generate_random_string(50)
            db.session.commit()

            # we use werzeug to validate user's password
            email_content = 'We heard that you lost your password. Sorry about that!<br /><br />'
            email_content += 'But don’t worry! You can use the following link to reset your password:<br /><br />'
            email_content += '<a href="' + url_for('users.reset_password', token=user.password_token, _external=True) + '">' + url_for('users.reset_password', token=user.password_token, _external=True) + '</a><br /><br />'
            #email_content += 'If you don’t use this link within 24 hours, it will expire. To get a new password reset link, visit ' + url_for('users.reset_password') + ' \n\n'
            email_content += 'Thanks,<br />'
            email_content += 'Sketchup Oulu team'

            send_mail([user.email], '[SketchupOulu] Reset your password‏', email_content)
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
    return redirect(url_for('index'))

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
    user.profile_picture = upload_picture(request.files['profile_picture'], 'static/images/profile_pictures')
    g.user = user
    db.session.commit()

    return url_for('static', filename='images/profile_pictures/' + user.profile_picture, _external=True)

@mod.route('/building_models/', methods=['GET', 'POST'])
@requires_login
def building_models():

    user = User.query.get(g.user.id)
    user.profile_picture = upload_picture(request.files['profile_picture'], 'static/images/profile_pictures')
    g.user = user
    db.session.commit()

    return url_for('static', filename='images/profile_pictures/' + user.profile_picture, _external=True)
