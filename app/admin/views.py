from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy import or_
from werkzeug import check_password_hash, generate_password_hash, secure_filename

import json, os

from app import db, app_dir, send_mail
from app.users.models import User, Group
from app.journal.models import JournalCategory, Journal
from app.admin.decorators import requires_admin
from app.admin.forms import UserSearchForm, SendEmailForm, CreateJournalCategoryForm, EditJournalCategoryForm, CreateJournalForm, EditJournalForm
import config
import app.utilities as utilities

mod = Blueprint('admin', __name__, url_prefix='/admin')

@mod.route('/user_management/')
@requires_admin
def user_management():
    form = UserSearchForm(request.form)
    groups = Group.query.all()
    return render_template("admin/user_management.html", form=form, groups=groups)

@mod.route('/user_list/', methods=['GET', 'POST'])
@requires_admin
def user_list():

    page = request.args.get('page', 1)

    form = UserSearchForm(request.form)
    users = []
    if form.is_submitted():
        post_data = form.user_info.data
        if post_data is None:
            post_data = ''
        user_query = User.query.filter(or_(User.email.like('%' + post_data + '%'),
                                      User.username.like('%' + post_data + '%'),
                                      User.fullname.like('%' + post_data + '%')))
    else:
        user_query = User.query

    page = user_query.paginate(page, 20, False)

    for user in page.items:
        users.append({'user_id': user.id,
                      'user_username': user.username,
                      'user_email': user.email,
                      'user_fullname': user.fullname})
    total_page = page.pages
    current_page = page.page

    return json.dumps({'users': users, 'total_page': total_page, 'current_page': current_page})

@mod.route('/get_user_info/', methods=['GET'])
@requires_admin
def get_user_info():

    user_id = request.args.get('user_id', 0)
    if user_id == 0:
        return json.dump({'error': 'User not found'}), 404

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dump({'error': 'User not found'}), 404

    groups = []
    for group in user.groups:
        groups.append(group.id)

    serialize_user = {'id': user.id,
                      'username': user.username,
                      'email': user.email,
                      'fullname': user.fullname,
                      'address': user.address,
                      'phone_number': user.phone_number,
                      'banned': user.banned,
                      'groups': groups}

    return json.dumps(serialize_user), 200

@mod.route('/update_user_info/', methods=['POST'])
@requires_admin
def update_user_info():

    user_id = request.form.get('user_id', 0)
    if user_id == 0:
        return json.dump({'error': 'User not found'}), 404

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dump({'error': 'User not found'}), 404

    fullname = request.form.get('fullname', '')
    address = request.form.get('address', '')
    banned = request.form.get('banned', '')

    #update basic information
    update_data = {}
    if fullname != '':
        update_data['fullname'] = fullname
    if address != '':
        update_data['address'] = address
    if banned != '':
        update_data['banned'] = banned
    User.query.filter_by(id=session.get('user_id')).update(update_data)

    #update groups
    groups_string = request.form.get('groups_value', '')
    if groups_string != '':
        user.groups.clear()
        group_ids = groups_string.split('|')
        for group_id in group_ids:
            group = Group.query.filter_by(id=group_id).first()
            if group is not None:
                user.groups.append(group)

    #commit to db
    db.session.commit()

    groups = []
    for group in user.groups:
        groups.append(group.id)

    serialize_user = {'id': user.id,
                      'username': user.username,
                      'email': user.email,
                      'fullname': user.fullname,
                      'address': user.address,
                      'phone_number': user.phone_number,
                      'banned': user.banned,
                      'groups': groups}

    return json.dumps(serialize_user), 200



@mod.route('/search_emails/', methods=['GET'])
@requires_admin
def search_emails():
    search_text = request.args.get('q', '')
    if search_text == '':
        return json.dumps([])

    users = []
    user_query = User.query.filter(or_(User.email.like('%' + search_text + '%'),
                                      User.username.like('%' + search_text + '%'),
                                      User.fullname.like('%' + search_text + '%')))

    for user in user_query.all():
        users.append({'id': user.email, 'name': user.username})

    return json.dumps(users)

@mod.route('/upload_image/', methods=['POST'])
@requires_admin
def upload_image():

    file = request.files['file']
    if file is None:
        return ''

    #generate filename
    original_filename_parts = file.filename.split('.')
    file_extension = original_filename_parts[len(original_filename_parts)-1]
    filename = utilities.generate_random_string(50) + '.' + file_extension
    filename = secure_filename(filename)

    #save file
    full_filename = os.path.join(app_dir, config.EMAIL_PICTURE, filename)
    file.save(full_filename)

    #return link to file
    return config.EMAIL_PICTURE_URL + filename

@mod.route('/send_email/', methods=['GET','POST'])
@requires_admin
def send_email():

    form = SendEmailForm(request.form)
    errors = []
    serialized_users = []

    if form.is_submitted():
        emails = form.emails.data.split(',')
        if form.validate():
            if form.action.data == 'send':
                send_mail(emails, form.title.data, form.content.data)
            else:
                send_mail([g.user.email], form.title.data, form.content.data)
        else:
            for error in form.emails.errors:
                errors.append(error)
            for error in form.title.errors:
                errors.append(error)
            for error in form.content.errors:
                errors.append(error)

        query_text = ''
        for index, email in enumerate(emails):
            if email != '':
                if index == 0:
                    query_text += "email='" + email + "'"
                else:
                    query_text += "or email='" + email + "'"
        users = User.query.filter(query_text).all()
        for user in users:
            serialized_users.append({'email': user.email, 'name': user.username})
        return render_template("admin/send_email.html", form=form, errors=errors, users=serialized_users)

    form.title.data = ''
    form.emails.data = ''
    form.content.data = ''
    return render_template("admin/send_email.html", form=form, errors=[])

@mod.route('/create_journal_category/', methods=['POST'])
@requires_admin
def create_journal_category():
    create_category_form = CreateJournalCategoryForm()
    errors = []
    if create_category_form.validate():
        category = JournalCategory(create_category_form.name.data, create_category_form.description.data)
        db.session.add(category)
        db.session.commit()
        return json.dumps({'success': True}), 201
    else:
        for error in create_category_form.name.errors:
            errors.append(error)
        return json.dumps(errors), 400

@mod.route('/edit_journal_category/', methods=['POST'])
@requires_admin
def edit_journal_category():
    edit_category_form = EditJournalCategoryForm()
    errors = []
    if edit_category_form.validate():
        category = JournalCategory.query.filter_by(id=edit_category_form.category_id.data).first()
        if category is None:
            return json.dumps(['Category not found']), 404

        category.name = edit_category_form.name.data
        category.description = edit_category_form.description.data
        db.session.commit()
        return json.dumps({'id': category.id, 'name': category.name}), 200
    else:
        for error in edit_category_form.name.errors:
            errors.append(error)
        for error in edit_category_form.category_id.errors:
            errors.append(error)
        return json.dumps(errors), 400

@mod.route('/get_category_data/', methods=['GET'])
@requires_admin
def get_category_data():
    category_id = request.args.get('category_id', 0)
    if category_id == 0:
        return json.dumps(['Category not found']), 404
    category = JournalCategory.query.filter_by(id=category_id).first()
    if category_id is None:
        return json.dumps(['Category not found']), 404

    return json.dumps({'id': category.id, 'name': category.name, 'description': category.description}), 200

@mod.route('/activate_deactivate_journal_category/', methods=['GET'])
@requires_admin
def activate_deactivate_journal_category():
    category_id = request.args.get('category_id', 0)
    if category_id == 0:
        return json.dumps(['Category not found']), 404
    category = JournalCategory.query.filter_by(id=category_id).first()
    if category_id is None:
        return json.dumps(['Category not found']), 404
    if category.is_activated == 1:
        category.is_activated = 0
    else:
        category.is_activated = 1
    db.session.commit()
    return json.dumps({'id': category.id, 'name': category.name, 'description': category.description, 'is_activated': category.is_activated}), 200

@mod.route('/delete_journal_category/', methods=['GET'])
@requires_admin
def delete_journal_category():
    category_id = request.args.get('category_id', 0)
    if category_id == 0:
        return json.dumps(['Category not found']), 404
    category = JournalCategory.query.filter_by(id=category_id).first()
    if len(category.get_journals()) > 0:
        return json.dumps(['Delete child journals first']), 400
    db.session.delete(category)
    db.session.commit()
    return json.dumps({'success': True}), 200

@mod.route('/news_management/', methods=['GET','POST'])
@requires_admin
def news_management():

    categories = JournalCategory.query.all()
    serialized_categories = []
    for category in categories:
        serialized_category = {}
        serialized_category['id'] = category.id
        serialized_category['name'] = category.name
        serialized_category['description'] = category.description
        serialized_category['is_activated'] = category.is_activated
        serialized_category['journals'] = []
        for journal in category.get_journals():
            serialized_journal = {}
            serialized_journal['id'] = journal.id
            serialized_journal['title'] = journal.id
            serialized_journal['content'] = journal.content
            serialized_journal['created_username'] = journal.created_user.username
            serialized_journal['post_time'] = journal.post_time
            serialized_journal['last_edited_username'] = journal.last_edited_user.username
            serialized_journal['last_edited_time'] = journal.last_edited_time
            serialized_journal['is_activated'] = journal.is_activated
            serialized_category['journals'].append(serialized_journal)
        serialized_category['total_page'] = category.total_page
        serialized_category['current_page'] = category.current_page
        serialized_categories.append(serialized_category)

    edit_category_form = EditJournalCategoryForm()
    create_category_form = CreateJournalCategoryForm()
    #create_journal_form = CreateJournalForm()
    #edit_journal_form = EditJournalForm()
    #edit_journal_form.news_category_id.choices = create_journal_form.news_category_id.choices = [(category.id, category.name) for category in JournalCategory.query.order_by('name')]

    return render_template("admin/news_management.html", categories=serialized_categories,
                           edit_category_form=edit_category_form,
                           create_category_form=create_category_form)

@mod.route('/create_journal/', methods=['GET','POST'])
@requires_admin
def create_journal():
    create_journal_form = CreateJournalForm()
    category_id = request.args.get('category_id', 0)
    errors = []
    create_journal_form.category_id.choices = [(category.id, category.name) for category in JournalCategory.query.order_by('name')]
    create_journal_form.category_id.choices.insert(0, (0, '===== Category ====='))
    if create_journal_form.is_submitted():
        create_journal_form.category_id.default = create_journal_form.category_id.data
    else:
        create_journal_form.category_id.default = category_id
    create_journal_form.process()

    return render_template("admin/create_journal.html", form=create_journal_form, errors=errors)