from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField,validators, DateField, HiddenField, TextAreaField, SelectField
from wtforms.validators import Required, EqualTo, Email, NoneOf

class UserSearchForm(Form):
    user_info = TextField('Info')

class SendEmailForm(Form):
    emails = TextField('Users', [Required(message='Insert users to send email')])
    title = TextField('Title', [Required(message='Email title is required')])
    content = TextAreaField('Content', [Required(message='Email content is required')])
    action = HiddenField('action')

class CreateJournalCategoryForm(Form):
    name = TextField('Name', [Required(message='Category name is required')])
    description = TextField('Description')

class EditJournalCategoryForm(Form):
    category_id = HiddenField('', [Required('Something went wrong...')])
    name = TextField('Name', [Required(message='Category name is required')])
    description = TextField('Description')

class CreateJournalForm(Form):
    title = TextField('Name', [Required(message='Category name is required')])
    content = TextField('Description')
    is_activate = BooleanField('Is activated')
    category_id = SelectField('Category', [Required('Select a category for the news'), NoneOf([0], 'Select a category for the news')], coerce=int)

class EditJournalForm(Form):
    title = TextField('Name', [Required(message='Category name is required')])
    content = TextField('Description')
    is_activate = BooleanField('Is activated')
    news_id = HiddenField('', [Required('Something went wrong...')])
    category_id = SelectField('Category', [Required('Select a category for the news'), NoneOf([0], 'Select a category for the news')],  coerce=int)