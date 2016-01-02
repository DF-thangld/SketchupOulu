import os
import sys

from flask import Flask, render_template, g, session
from flask_sqlalchemy import SQLAlchemy
from smtplib import SMTP, SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from validate_email import validate_email

import config

app = Flask(__name__)
app.config.from_object('config')

app_dir = os.path.dirname(os.path.realpath(__file__))

db = SQLAlchemy(app)

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
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('homepage.html'), 200


from app.users.views import mod as usersModule
from app.admin.views import mod as adminModule
app.register_blueprint(adminModule)
app.register_blueprint(usersModule)

# Later on you'll import the other blueprints the same way:
#from app.comments.views import mod as commentsModule
#from app.posts.views import mod as postsModule
#app.register_blueprint(commentsModule)
#app.register_blueprint(postsModule)