from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, make_response
from sqlalchemy import or_
from werkzeug import check_password_hash, generate_password_hash, secure_filename
from flask.ext.babel import gettext


import json, os
import datetime

from app import db, app_dir, send_mail
from app.users.models import User, Group
from app.sketchup.models import Scenario, BuildingModel
from app.journal.models import JournalCategory, Journal, JournalContent
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


@mod.route('/login_as/<user_id>', methods=['GET'])
@requires_admin
def login_as(user_id):

    if not user_id or user_id == 0:
        return render_template("404.html"), 404

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return render_template("404.html"), 404
    
    session['user_id'] = user_id
    return make_response(redirect(url_for('users.own_profile')))


@mod.route('/get_user_info/', methods=['GET'])
@requires_admin
def get_user_info():

    user_id = request.args.get('user_id', 0)
    if user_id == 0:
        return json.dump({'error': gettext('User not found')}), 404

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dump({'error': gettext('User not found')}), 404

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
        return json.dump({'error': gettext('User not found')}), 404

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dump({'error': gettext('User not found')}), 404

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
    User.query.filter_by(id=user_id).update(update_data)

    #update groups
    groups_string = request.form.get('groups_value', '')
    if groups_string != '':
        for i in range(0, len(user.groups)):
            user.groups.remove(user.groups[0])
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
    full_filename = os.path.join(config.email_picture_dir, filename)
    file.save(full_filename)

    #return link to file
    return url_for('static', filename='images/email_pictures/' + filename, _external=True)

@mod.route('/send_email/', methods=['GET','POST'])
@requires_admin
def send_email():

    form = SendEmailForm(request.form)
    errors = []
    serialized_users = []

    if form.is_submitted():
        is_validated = True
        emails = form.emails.data.split(',')
        
        if len(emails) == 0:
            is_validated = False
            errors.append(gettext("Insert users to send email"))
        if form.title.data.strip() == '':
            is_validated = False
            errors.append(gettext("Email title is required"))
        if form.content.data.strip() == '':
            is_validated = False
            errors.append(gettext("Email content is required"))
        
        if is_validated:
            if form.action.data == 'send':
                send_mail(emails, form.title.data, form.content.data)
            else:
                send_mail([g.user.email], form.title.data, form.content.data)

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
    
    is_validated = True
    if create_category_form.name.data.strip() == '':
        is_validated = False
        errors.append(gettext("Category name is required"))
    if is_validated:
        category = JournalCategory(create_category_form.name.data, create_category_form.description.data)
        db.session.add(category)
        db.session.commit()
        return json.dumps({'success': True}), 201
    else:
        return json.dumps(errors), 400

@mod.route('/edit_journal_category/', methods=['POST'])
@requires_admin
def edit_journal_category():
    edit_category_form = EditJournalCategoryForm()
    errors = []
    
    if edit_category_form.name.data.strip() == '':
        errors.append(gettext('Category name is required'))
    if edit_category_form.category_id.data is None or edit_category_form.name.data.strip() == '':
        errors.append(gettext('Something went wrong...'))
    
    if len(errors) == 0:
        category = JournalCategory.query.filter_by(id=edit_category_form.category_id.data).first()
        if category is None:
            return json.dumps([gettext('Category not found')]), 404

        category.name = edit_category_form.name.data
        category.description = edit_category_form.description.data
        db.session.commit()
        return json.dumps({'id': category.id, 'name': category.name}), 200
    else:
        return json.dumps(errors), 400

@mod.route('/get_category_data/', methods=['GET'])
@requires_admin
def get_category_data():
    category_id = request.args.get('category_id', 0)
    if category_id == 0:
        return json.dumps([gettext('Category not found')]), 404
    category = JournalCategory.query.filter_by(id=category_id).first()
    if category_id is None:
        return json.dumps([gettext('Category not found')]), 404

    return json.dumps({'id': category.id, 'name': category.name, 'description': category.description}), 200

@mod.route('/activate_deactivate_journal_category/', methods=['GET'])
@requires_admin
def activate_deactivate_journal_category():
    category_id = request.args.get('category_id', 0)
    if category_id == 0:
        return json.dumps([gettext('Category not found')]), 404
    category = JournalCategory.query.filter_by(id=category_id).first()
    if category_id is None:
        return json.dumps([gettext('Category not found')]), 404
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
        return json.dumps([gettext('Category not found')]), 404
    category = JournalCategory.query.filter_by(id=category_id).first()
    if len(category.get_journals()) > 0:
        return json.dumps([gettext('Delete child journals first')]), 400
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
            serialized_journal['title'] = journal.title
            serialized_journal['content'] = journal.content
            serialized_journal['created_username'] = journal.created_user.username
            serialized_journal['post_time'] = journal.post_time
            if journal.last_edited_user is not None:
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
        
    if create_journal_form.title.data.strip() == '':
        errors.append(gettext('Journal name is required'))
    if create_journal_form.title.data is None or create_journal_form.title.data.strip() == '' or create_journal_form.title.data.strip() == '0':
        errors.append(gettext('Category is required'))

    if not create_journal_form.is_submitted():
        create_journal_form.is_activate.checked = True
        create_journal_form.process()
        return render_template("admin/create_journal.html", form=create_journal_form, errors=errors, languages=config.LANGUAGES)
    elif not len(errors) == 0:

        return render_template("admin/create_journal.html", form=create_journal_form, errors=errors, languages=config.LANGUAGES)
    elif len(errors) == 0:
        # create journal
        journal_activated = 0
        if create_journal_form.is_activate.data:
            journal_activated = 1
        category = JournalCategory.query.filter_by(id=create_journal_form.category_id.data).first()
        if category is None:
            errors.append(gettext('Category is required'))
            return render_template("admin/create_journal.html", form=create_journal_form, errors=errors, languages=config.LANGUAGES)

        journal = Journal(create_journal_form.title.data, create_journal_form.content.data, g.user, category, journal_activated)
        for language in config.LANGUAGES:
            title_language = request.form.get('title_' + language, '')
            content_language = request.form.get('content_' + language, '')
            journal_content = JournalContent(title_language, content_language, journal, language)
            db.session.add(journal_content)

        db.session.add(journal)
        db.session.commit()
        #redirect to journal page
        return redirect(url_for('admin.edit_journal', journal_id=journal.id))

@mod.route('/delete_journal/', methods=['GET'])
@requires_admin
def delete_journal():
    journal_id = request.args.get('journal_id', 0)
    if journal_id == 0:
        return json.dumps([gettext('Journal not found')]), 404
    journal = Journal.query.filter_by(id=journal_id).first()
    if journal is None:
        return json.dumps([gettext('Journal not found')]), 404

    for content in journal.journal_contents:
        db.session.delete(content)
    db.session.delete(journal)

    db.session.commit()
    return json.dumps({'success': True}), 200

@mod.route('/activate_deactivate_journal/', methods=['GET'])
@requires_admin
def activate_deactivate_journal():
    journal_id = request.args.get('journal_id', 0)
    if journal_id == 0:
        return json.dumps([gettext('Journal not found')]), 404
    journal = Journal.query.filter_by(id=journal_id).first()
    if journal is None:
        return json.dumps([gettext('Journal not found')]), 404

    if journal.is_activated == 1:
        journal.is_activated = 0
    else:
        journal.is_activated = 1
    db.session.commit()
    return json.dumps({'id': journal.id, 'title': journal.title, 'is_activated': journal.is_activated}), 200

@mod.route('/edit_journal/', methods=['GET','POST'])
@requires_admin
def edit_journal():

    journal_id = request.args.get('journal_id', 0)
    if journal_id == 0:
        return render_template('404.html'), 404

    journal = Journal.query.filter_by(id=journal_id).first()
    if journal is None:
        return render_template('404.html'), 404

    edit_journal_form = EditJournalForm()
    errors = []
    edit_journal_form.category_id.choices = [(category.id, category.name) for category in JournalCategory.query.order_by('name')]
    edit_journal_form.category_id.choices.insert(0, (0, gettext('===== Category =====')))

    journal_content_objs = journal.journal_contents
    journal_contents = {}
    for journal_content_obj in journal_content_objs:
        journal_contents[journal_content_obj.locale] = journal_content_obj.to_dict()
    for language in config.LANGUAGES:
        if language not in journal_contents:
            journal_contents[language] = {  'locale': language,
                                            'content': '',
                                            'title': ''}

    if not edit_journal_form.is_submitted():
        edit_journal_form.category_id.default = journal.category.id
        edit_journal_form.is_activate.checked = (journal.is_activated == 1)
        edit_journal_form.process()
        edit_journal_form.title.data = journal.title
        edit_journal_form.content.data = journal.content

        return render_template("admin/edit_journal.html", journal_id=journal_id, form=edit_journal_form, errors=errors, languages=config.LANGUAGES, journal_contents=journal_contents), 200
    else:
        
        if edit_journal_form.title.data.strip() == '':
            errors.append(gettext('Journal name is required'))
        if edit_journal_form.title.data is None or edit_journal_form.title.data.strip() == '' or edit_journal_form.title.data.strip() == '0':
            errors.append(gettext('Category is required'))
        
        for language in config.LANGUAGES:
            if language not in journal_contents:
                journal_contents[language] = {  'locale': language,
                                                'content': '',
                                                'title': ''}
            if ('title_' +  language) in request.form:
                journal_contents[language]['title'] = request.form.get('title_' + language)
            if ('content_' +  language) in request.form:
                journal_contents[language]['content'] = request.form.get('content_' + language)

        if len(errors) == 0:
            category = JournalCategory.query.filter_by(id=edit_journal_form.category_id.data).first()
            if category is None:
                errors.append(gettext('Journal category not found'))
                return render_template("admin/edit_journal.html", journal_id=journal_id, form=edit_journal_form, errors=errors, languages=config.LANGUAGES, journal_contents=journal_contents), 400
            journal.category = category
            journal.title = edit_journal_form.title.data
            journal.content = edit_journal_form.content.data

            journal_activated = 0
            if edit_journal_form.is_activate.data:
                journal_activated = 1
            journal.is_activated = journal_activated
            journal.last_edited_user = g.user
            journal.last_edited_time = datetime.datetime.now()

            for i in range(0, len(journal.journal_contents)):
                journal.journal_contents.remove(journal.journal_contents[0])
            for language in journal_contents:
                jc = JournalContent(journal_contents[language]['title'], journal_contents[language]['content'], journal, language)
            db.session.commit()
            return render_template("admin/edit_journal.html", journal_id=journal_id, form=edit_journal_form, errors=errors, languages=config.LANGUAGES, journal_contents=journal_contents), 200
        else:
            return render_template("admin/edit_journal.html", journal_id=journal_id, form=edit_journal_form, errors=errors, languages=config.LANGUAGES, journal_contents=journal_contents), 400


@mod.route('/change_base_scenario_status/<scenario_id>', methods=['GET'])
@requires_admin
def change_base_scenario_status(scenario_id):
    errors = []
    if scenario_id == '':
        return json.dumps([gettext('Scenario not found')]), 404

    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if scenario is None:
        return json.dumps([gettext('Scenario not found')]), 404
    if scenario.is_base_scenario == 1:
        scenario.is_base_scenario = 0
    else:
        scenario.is_base_scenario = 1

    db.session.commit()

    return json.dumps({'new_status': scenario.is_base_scenario}), 200
