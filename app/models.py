from app import app

from app import db 

from hashlib import md5

import sys

if sys.version_info >= (3, 0):

    enable_search = False

else:

    enable_search = True


    import flask_whooshalchemy as whooshalchemy



''' Since this is an auxiliary table that has no data 
other than the foreign keys, we use the lower level APIs in 
flask-sqlalchemy to create the table without an associated model '''

followers = db.Table ('followers',
                     db.Column ('follower_id', 
                                db.Integer, db.ForeignKey ('user.id')),
                     db.Column ('followed_id',
                               db.Integer, db.ForeignKey ('user.id'))
                     )



class User (db.Model):

    id = db.Column (db.Integer, primary_key = True)

    nickname = db.Column (db.String(64), index = True, unique = True)

    email = db.Column (db.String(120), index = True, unique = True)

    posts = db.relationship ('Post', backref = 'author', lazy = 'dynamic')

    about_me = db.Column (db.String (140))

    last_seen = db.Column (db.DateTime)

    ''' A many-to-many relationship (which is self-referential) 
    i.e. Many-Users-to-Many-Users (User has followers, and is followed)
    We will be linking User instances to other User instances, so as 
    a convention, let's say that for a pair of linked users in this 
    relationship -- the left side `user` is //following// the right side
    `user`.
    We define the relationship as seen from the left side entity with
    the name `followed`, because when we query the relationship from the
    left side -- we will get the list of followed users. '''

    ''' Argumnets to db.relationship() exlpanations:

        'User': right-side entity, left is parent
        secondary: indicates the association table used for this relationship
        primaryjoin: indicates condition that links left side entity with 
            association table
            Since followers table isn't model there is odd syntax required for 
            field
        secondaryjoin: indicates condition that links right side entity 
            (followed) to association
        backref: Defines how this relationship will be accessed from the 
            right side entity 
            For a given user, the query named `followed` returns all the right 
            side users that have the target user on the left side
            The back-reference will be called `followers` and will return all the left side users that are linked to the target user in the 
            right side
            The additional lazy argument indicates the execution mode for this
            query
            A mode of dynamic sets up the query to not run until specifically 
            requested
            This is important for performace, but also because we will be able 
            to take this query and modify it before it executes... more about 
            this later
        lazy: Similar to the parameter of the same name in the `backref`, 
                but this one applies to the regular query instead of the 
                back reference '''
    followed = db.relationship ('User', 
                               secondary=followers, 
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    @property
    def is_authenticated (self):

        return True


    @property 
    def is_active (self):

        return True
    

    @property
    def is_anonymous (self):

        return False


    def get_id (self):

        try:

            return unicode (self.id) # python 2
        
        except NameError:

            return str (self.id) # python 3



    def follow (self, user):

        if not self.is_following (user):

            self.followed.append (user)

            return self


    def unfollow (self, user):

        if self.is_following (user):

            self.followed.remove (user)

            return self


    ''' Taking the `followed` relationship query (which returns all the 
    [follower, followed] pairs that have our user as the `follower`), and
    we filter it by the `followed` user. This is possible because the 
    `followed` relationship has a lazy mode of //dynamic//, so instead of being
    the result of the query, this is the actual //query object//, before 
    exectuion.
    The return from the `filter` call is the modified query, still without
    having executed.
    So we then call count () on this query, and now the query will execute and
    return the number of records found '''
    def is_following (self, user):

        return self.followed.filter (
            followers.c.followed_id == user.id).count () > 0



    def followed_posts (self):

        ''' Three parts: the //join//, the //filter//, and the //order_by// 
        The `join` operation is called on the `Post` table
        There are two arguments: the first is another table, our `followers`
        table. The second argument to join call is the //join condition//
        Join operation will create a temporary new table with data from the
        `Post` and `followers` table, merged according to the given condition
        we want the field `followed_id` of the `followers` table to match the
        `user_id` field of the `Post` table'''
        return Post.query.join (followers, (
            followers.c.followed_id == Post.user_id)).filter (
                followers.c.follower_id == self.id).order_by (
                    Post.timestamp.desc ()
                )



    ''' Get a user avatar using Gravatar service
    if the user's email does not correspond to gravtar account, 
    a dfeault avatar is created using the d=retro option '''
    def avatar (self, size):

        return 'http://www.gravatar.com/avatar/%s?d=retro&s=%d' % (
            md5 (self.email.encode('utf-8')).hexdigest(), size)



    ''' In the event that a user attempts to create an account with a 
    nickname of another user, automatically append a version number 
    Seems a bit like a [Hack] '''
    @staticmethod
    def make_unique_nickname (nickname):

        if User.query.filter_by (nickname=nickname).first() is None:

            return nickname


        version = 2


        while True:

            new_nickname = nickname + str (version)


            if User.query.filter_by (nickname=new_nickname).first() is None:

                break


            version += 1


        return new_nickname



    def __repr__ (self):

        return '<User %r>' % (self.nickname)



class Post (db.Model):

    __searchable__ = ['body']


    id = db.Column (db.Integer, primary_key = True)

    body = db.Column (db.String (140))

    timestamp = db.Column (db.DateTime)

    user_id = db.Column (db.Integer, db.ForeignKey ('user.id'))


    def __repr__ (self):

        return '<Post %r>' % (self.body)



if enable_search:

    whooshalchemy.whoosh_index (app, Post)
