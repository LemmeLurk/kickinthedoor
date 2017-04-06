import os



basedir = os.path.abspath (os.path.dirname (__file__))


# pagination
POSTS_PER_PAGE = 3


WHOOSH_BASE = os.path.join (basedir, 'search.db')


MAX_SEARCH_RESULTS = 50


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join (basedir, 'app.db')

SQLALCHEMY_MIGRATE_REPO = os.path.join (basedir, 'db_repository')


WTF_CSRF_ENABLED = True

SECRET_KEY = 'you-will-never-guess'


OPENID_PROVIDERS = [
    {'name': 'Blogspot', 'url':'https://www.blogspot.com/'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}
]


# mail server settings

'''MAIL_SERVER = 'localhost'

MAIL_PORT = 25

MAIL_USERNAME = None

MAIL_PASSWORD = None


# administrator list
ADMINS = ['you@example.com']'''


MAIL_SERVER = 'smtp.gmail.com'

MAIL_PORT = 465

MAIL_USE_TLS = False

MAIL_USE_SSL = True

MAIL_USERNAME = os.environ.get ('MAIL_USERNAME')

MAIL_PASSWORD = os.environ.get ('MAIL_PASSWORD')


ADMINS = ['oh.vinxi@gmail.com']


SQLALCHEMY_TRACK_MODIFICATIONS = False
