import os
_basedir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(_basedir, 'app')
email_picture_dir = os.path.join(app_dir, 'static/images/email_pictures/')
user_profile_dir = os.path.join(app_dir, 'static/images/profile_pictures/')
building_model_dir = os.path.join(app_dir, 'static/models/building_models/')
scenario_dir = os.path.join(app_dir, 'static/models/scenario_models/')

DEBUG = False

ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

SQLALCHEMY_DATABASE_URI = 'Database connection string'
SQLALCHEMY_TRACK_MODIFICATIONS = False

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 20

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_OPTIONS = {'theme': 'white'}

EMAIL = {'from': 'Email name',
         'address': 'Email address',
         'password': 'Email password',
         'smtp_server': 'SMTP server',
         'smtp_port': SMTP port}

EMAIL_PICTURE = os.path.join('static', 'images', 'email_pictures')
EMAIL_PICTURE_URL = BASE_URL + 'static/images/email_pictures/'

LANGUAGES = {
    'en': 'English',
    'fi': 'Suomea'
}

ALLOWED_FILE_TYPES = ['zip', 'jpg', 'jpeg', 'png']

BABEL_DEFAULT_LOCALE = 'en'
DEFAULT_LOCALE = 'fi'
