from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField,validators, DateField, HiddenField, TextAreaField
from wtforms.validators import Required, EqualTo, Email

class UserSearchForm(Form):
    user_info = TextField('Info')

class SendEmailForm(Form):
    emails = TextField('Users', [Required(message='Insert users to send email')])
    title = TextField('Title', [Required(message='Email title is required')])
    content = TextAreaField('Content', [Required(message='Email content is required')])
    action = HiddenField('action')