import os
import sys
import datetime
import logging
from base64 import decodestring, b64decode

from flask import Flask, render_template, g, session, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from smtplib import SMTP, SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from validate_email import validate_email
from werkzeug import secure_filename

import config
import app.utilities as utilities

app = Flask(__name__)
app.config.from_object('config')

babel = Babel(app)

app_dir = os.path.dirname(os.path.realpath(__file__))

db = SQLAlchemy(app)

@babel.localeselector
def get_babel_locale():
    #TODO: change language back
    return 'en' #session['locale']

@app.before_request
def check_locale():
    #TODO: change language back
    if 'lang' in request.args:
        locale = request.args.get('lang')
        if locale in config.LANGUAGES:
            session['locale'] = locale
            return redirect(request.url.replace('lang=' + locale, ''))
        else:
            session['locale'] = config.DEFAULT_LOCALE
    elif 'locale' not in session:
        locale = request.accept_languages.best_match(config.LANGUAGES.keys())
        if locale is None:
            locale = config.DEFAULT_LOCALE
        session['locale'] = locale #locale
    elif 'locale' in session and (session['locale'] is None or session['locale'] not in config.LANGUAGES.keys()):
        session['locale'] = config.DEFAULT_LOCALE

@app.before_request
def good_url():
    if request.url[-1:] == '&' or request.url[-1:] == '?':
        return redirect(request.url[:-1])

def upload_file(upload_file, stored_directory, generate_filename=True, file_type="image"):
    original_filename_parts = upload_file.filename.split('.')
    original_filename = original_filename_parts[0]
    for i in range(1, len(original_filename_parts)-1):
        original_filename += '.' + original_filename_parts[i]
    file_extension = original_filename_parts[len(original_filename_parts)-1]
    file_extension = file_extension.lower()
    if generate_filename:
        filename_without_extension = utilities.generate_random_string(50)
        filename = filename_without_extension + '.' + file_extension
    else:
        filename_without_extension = original_filename
        filename = upload_file.filename
    filename = secure_filename(filename)

    #save file
    full_filename = os.path.join(app_dir, stored_directory, filename)
    upload_file.save(full_filename)

    return {'filename': filename,
            'extension': file_extension.lower(),
            'original_filename': original_filename,
            'full_filename': full_filename,
            'filename_without_extension': filename_without_extension}

def save_image(image_filename, image_dir, base64_content):
    fh = open(os.path.join(app_dir, image_dir, image_filename), "wb")
    
    b64data = base64_content.split(',')[1] # [sic]
    fh.write(b64decode(b64data))
    
    #fh.write(decodestring(base64_content))
    fh.close()
    
def delete_file(dir, filename):
    try:
        os.remove(os.path.join(app_dir, dir, filename))
        return True
    except:
        return False

def send_mail(emails, title, content):

    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = title
    msgRoot['From'] = config.EMAIL['from']
    msgRoot['To'] = 'df.thangld@hotmail.com'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(content, 'html')
    msgAlternative.attach(msgText)

    smtp = SMTP_SSL(config.EMAIL['smtp_server'] + ':' + str(config.EMAIL['smtp_port']))
    smtp.login(config.EMAIL['address'], config.EMAIL['password'])
    for email in emails:
        if validate_email(email):
            smtp.sendmail(config.EMAIL['address'], email, msgRoot.as_string())
    smtp.quit()

########################
# Configure Secret Key #
########################
def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
    in the instance directory.

    If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.
    """
    filename = os.path.join(app.instance_path, filename)

    try:
        #app.config['SECRET_KEY'] = open(filename, 'rb').read()
        app.config['SECRET_KEY'] = config.SECRET_KEY
    except IOError:
        print('Error: No secret key. Create it with:')
        full_path = os.path.dirname(filename)
        if not os.path.isdir(full_path):
            print('mkdir -p {filename}'.format(filename=full_path))
        print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
        sys.exit(1)

if not app.config['DEBUG']:
    install_secret_key(app)

@app.errorhandler(404)
def not_found(error):
    if request.endpoint != 'static':
        return render_template('404.html'), 404
    else:
        return '', 404

@app.route('/')
def index():
    return render_template('homepage.html'), 200

@app.route('/static/js/constants.js')
def constants_js():
    return render_template('constants.js'), 200

@app.route('/404')
def page_not_found():
    print(request.url)
    return render_template('404.html'), 404

from app.users.views import mod as usersModule
from app.admin.views import mod as adminModule
from app.journal.views import mod as journalModule
from app.sketchup.views import mod as sketchupModule

app.register_blueprint(adminModule)
app.register_blueprint(usersModule)
app.register_blueprint(journalModule)
app.register_blueprint(sketchupModule)

# Later on you'll import the other blueprints the same way:
#from app.comments.views import mod as commentsModule
#from app.posts.views import mod as postsModule
#app.register_blueprint(commentsModule)
#app.register_blueprint(postsModule)