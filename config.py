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

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sketchup_oulu:abcxyz@vm0106.virtues.fi:7557/sketchup_oulu'
SQLALCHEMY_TRACK_MODIFICATIONS = False

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LcHiRUTAAAAAK7lmJkVHe8S1_VR51Q3qXTwAu5W'
RECAPTCHA_PRIVATE_KEY = '6LcHiRUTAAAAALLUalMoISvzOLt35PwQoRT1-4KG'
RECAPTCHA_OPTIONS = {'theme': 'white'}

EMAIL = {'from': 'Sketchup Oulu <sketchup_oulu@hotmail.com>',
         'address': 'oulu.city.designer@gmail.com',
         'password': 'abcxyz@123',
         'smtp_server': 'smtp.gmail.com',
         'smtp_port': 465}

EMAIL_PICTURE = os.path.join('static', 'images', 'email_pictures')
BASE_URL = 'http://localhost:5000/'
EMAIL_PICTURE_URL = BASE_URL + 'static/images/email_pictures/'