from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField,validators, DateField, HiddenField, TextAreaField, FileField
from wtforms.validators import Required, EqualTo, Email

class LoginForm(Form):
    email = TextField('Email', [Required(message='Email is required'), Email(message='Invalid email address')])
    password = PasswordField('Password', [Required(message='Password field is required')])

class RegisterForm(Form):
    name = TextField('Username', [Required(message='Username is required')])
    email = TextField('Email address', [Required(message='Email is required'), Email(message='Invalid email address')])
    password = PasswordField('Password', [Required(message='Password is required')])
    confirm = PasswordField('Repeat Password', [
                                                Required(message='You have to confirm your password'),
                                                EqualTo('password', message='Passwords must match')
                                                ])
    recaptcha = RecaptchaField()

class UserProfileForm(Form):
    username = TextField('Username', [Required(message='Username is required')])
    email = TextField('Email address', [Required(message='Email is required'), Email(message='Invalid email address')])
    fullname = TextField()
    address = TextField()
    postal_code = TextField()
    phone_number = TextField()

class ResetPasswordForm(Form):
    email = TextField('Enter your email address and we will send you a link to reset your password', [Required(message='Email is required'), Email(message='Invalid email address')])