from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash

from app import db
from app.users.forms import RegisterForm, LoginForm, UserProfileForm
from app.users.models import User
from app.users.decorators import requires_login

mod = Blueprint('users', __name__, url_prefix='/users')

@mod.route('/profile/')
@requires_login
def profile():
    return render_template("users/profile.html", user=g.user)

@mod.before_request
def before_request():
    """
    pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])  # @UndefinedVariable

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
            if user and check_password_hash(user.password, form.password.data):
                # the session can't be modified as it's signed,
                # it's a safe place to store the user id
                session['user_id'] = user.id
                g.user = user
                flash('Welcome %s' % user.username)
                return redirect(url_for('users.profile'))

            #login fail for whatever reason

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
    
    #test_user = User.query.filter_by(id=1)

    
    form = RegisterForm(request.form)
    errors = []

    if form.is_submitted():
        if form.validate():
            # create an user instance not yet stored in the database
            user = User(username=form.name.data, email=form.email.data,
              password=generate_password_hash(form.password.data))

            same_username_user = User.query.filter_by(username=form.name.data).first()
            same_email_user = User.query.filter_by(email=form.email.data).first()
            if same_email_user is None:
                errors.append('Duplicate email address')
            if same_username_user is None:
                errors.append('Duplicate username address')

            if len(errors) > 0:
                return render_template("users/register.html", form=form, errors=errors)

            # Insert the record in our database and commit it
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
    return "TODO"

@mod.route('/logout/', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@mod.route('/user_profile/', methods=['GET', 'POST'])
def user_profile():
    form = UserProfileForm()


    if form.is_submitted():

        User.query.filter_by(id=session.get('user_id')).update(dict(fullname=form.fullname.data,
                                                                            address=form.address.data,
                                                                            phone_number=form.phone_number.data))
        db.session.commit()

        user = User.query.filter_by(id=session.get('user_id')).first()
        user.fullname = form.fullname.data
        user.address = form.address.data
        user.phone_number = form.phone_number.data

        g.user = user

    form.email.data = g.user.email
    form.username.data = g.user.username
    form.fullname.data = g.user.fullname
    form.address.data = g.user.address
    form.phone_number.data = g.user.phone_number
    #form.birthdate.data = g.user.birthdate

    return render_template("users/user_profile.html", form=form)