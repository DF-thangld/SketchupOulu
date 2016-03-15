from flask.ext.wtf import Form, RecaptchaField
from flask.ext.babel import gettext
from wtforms import TextField, PasswordField, BooleanField,validators, DateField, HiddenField, TextAreaField, FileField
from wtforms.validators import Required, EqualTo, Email

class LoginForm(Form):

    email = TextField(label=gettext('Email'), validators=[Required(message=gettext('Email is required')), Email(message=gettext('Invalid email address'))], default='')
    password = PasswordField(label=gettext('Password'), validators=[Required(message=gettext('Password field is required'))], default='')

class RegisterForm(Form):
    name = TextField(label=gettext('Username'), validators=[Required(message=gettext('Username is required'))], default='')
    email = TextField(gettext('Email address'), [Required(message=gettext('Email is required')), Email(message=gettext('Invalid email address'))], default='')
    password = PasswordField(gettext('Password'), [Required(message=gettext('Password is required'))], default='')
    confirm = PasswordField(gettext('Repeat Password'), [
                                                Required(message=gettext('You have to confirm your password')),
                                                EqualTo('password', message=gettext('Passwords must match'))
                                                ], default='')
    recaptcha = RecaptchaField()

class UserProfileForm(Form):
    username = TextField(gettext('Username'), [Required(message=gettext('Username is required'))])
    email = TextField(gettext('Email address'), [Required(message='Email is required'), Email(message=gettext('Invalid email address'))])
    fullname = TextField(default='')
    address = TextField(default='')
    postal_code = TextField(default='')
    phone_number = TextField(default='')

class ResetPasswordForm(Form):
    email = TextField(gettext('Enter your email address and we will send you a link to reset your password'), [Required(message=gettext('Email is required')), Email(message=gettext('Invalid email address'))], default='')