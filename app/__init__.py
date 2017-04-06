import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_openid import OpenID

from flask_mail import Mail

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, \
        MAIL_PASSWORD


app = Flask (__name__)

app.config.from_object ('config')


db = SQLAlchemy (app)


lm = LoginManager ()

lm.init_app (app)

# used to redirect user to login when try to access page that requires login
lm.login_view = 'login' 


oid = OpenID (app, os.path.join (basedir, 'tmp'))

mail = Mail (app)


''' Enable emailing Admin exceptions when debugging is disabled '''
if not app.debug:

    import logging

    from logging.handlers import SMTPHandler, RotatingFileHandler

    ''' Limit size of log to 1mb, and keep only last 10 logs '''
    file_handler  = RotatingFileHandler ('tmp/microblog.log', 'a', \
                                        1 * 1024 * 1024, 10)

    file_handler.setFormatter (logging.Formatter (
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))


    app.logger.setLevel (logging.INFO)

    file_handler.setLevel (logging.INFO)

    app.logger.addHandler (file_handler)

    app.logger.info ('microblog startup')


    credentials = None


    if MAIL_USERNAME or MAIL_PASSWORD:

        credentials = (MAIL_USERNAME, MAIL_PASSWORD)


    mail_handler = SMTPHandler ((MAIL_SERVER, MAIL_PORT), \
                                'oh.vinxi@gmail.com',\
                               ADMINS, 'microblog failure',\
                               credentials)

    mail_handler.setLevel (logging.ERROR)

    app.logger.addHandler (mail_handler)


""" Avoid circular import error 
    views calls on __name__.app """

from app import views, models
