from app import db, models

u = models.User(nickname='John', email='john@email.com')

db.session.add (u)

db.session.commit ()

u = modles.User (nickname = 'susan', email='susan@email.com')

db.session.add (u)

db.session.commit()

# Now we can query what our users are:
users = models.User.query.all()

users # [<User u'John'>,<User u'susan'>]


for u in users:
    print (u.id, u.nickname)

# 1 John
# 2 susan


# use id of a user to find the data for that user
u = models.User.query.get(1)

u # <User u'John'>

# Now add blog post

import datetime

p = models.Post (body='my first post!', timestamp=datetime.datetime.utcnow(),\
                author=u)

db.session.add(p)

db.session.commit()


# get all posts from user

posts = u.posts.all()


posts # [<Post u'my first post!'>]


# obtain author of each post
for p in posts:
    print (p.id, p.author.nickname, p.body)


