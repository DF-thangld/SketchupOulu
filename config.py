import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sketchup_oulu:abcxyz@vm0106.virtues.fi:7557/sketchup_oulu'

DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
RECAPTCHA_OPTIONS = {'theme': 'white'}