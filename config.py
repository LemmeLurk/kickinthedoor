# -*- coding: utf8 -*-


import os



basedir = os.path.abspath (os.path.dirname (__file__))


# pagination
POSTS_PER_PAGE = 3


WHOOSH_BASE = os.path.join (basedir, 'search.db')


MAX_SEARCH_RESULTS = 50


# available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}


# microsoft translation service
MS_TRANSLATOR_CLIENT_ID = 'smelting_post'

MS_TRANSLATOR_CLIENT_SECRET = 'tDGfxT/piu4htfP3lRPIvlsavVTppSQ8oqq4Muk+eBo='


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join (basedir, 'app.db')

SQLALCHEMY_MIGRATE_REPO = os.path.join (basedir, 'db_repository')


SQLALCHEMY_RECORD_QUERIES = True


# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5


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

MAIL_SERVER = 'localhost'

MAIL_PORT = 25

MAIL_USERNAME = None

MAIL_PASSWORD = None


# administrator list
ADMINS = ['you@example.com']


SQLALCHEMY_TRACK_MODIFICATIONS = False
