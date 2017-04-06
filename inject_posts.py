#!flask/bin/python


from app.models import User, Post

from app import db

import datetime


u = User.query.get(1)

p = Post(body='If I were a man', timestamp=datetime.datetime.utcnow (), \
         author=u)

db.session.add (p)

p = Post(body='and you a dog', timestamp=datetime.datetime.utcnow (), \
         author=u)

db.session.add (p)

p = Post(body='I\'d throw a stiick foor yoou', \
         timestamp=datetime.datetime.utcnow (), author=u)

db.session.add (p)


db.session.commit ()
