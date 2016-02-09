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
    title = TextField('Name (for admin view only) - Required', [Required(message='Journal name is required')], default='')
    content = TextAreaField('Description (for admin view only) - Required', [Required(message='Journal description is required')], default='')
    is_activate = BooleanField('Is activated', default=1)
    category_id = SelectField('Category', [Required('Category is required'), NoneOf([0], 'Category is required')], coerce=int)

class EditJournalForm(Form):
    title = TextField('Name (for admin view only)', [Required(message='Journal name is required')], default='')
    content = TextAreaField('Description (for admin view only)', [Required(message='Journal description is required')], default='')
    is_activate = BooleanField('Is activated', default=1)
    category_id = SelectField('Category', [Required('Category is required'), NoneOf([0], 'Category is required')],  coerce=int)