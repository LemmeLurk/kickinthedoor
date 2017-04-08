#!flask/bin/python

# -*- coding: utf8 -*-

import os

import unittest

from datetime import datetime, timedelta

from config import basedir

from app import app, db

from app.models import User, Post

from app.translate import microsoft_translate



class TestCase (unittest.TestCase):

    ''' Run before each Test '''

    def setUp (self):

        app.config['TESTING'] = True

        app.config['WTF_CSRF_ENABLED'] = False

        app.config['SQLALCHEMY_DATABASE_URI'] = \
                'sqlite:///' + os.path.join (basedir, 'test.db')

        self.app = app.test_client ()

        db.create_all ()



    ''' Run after each test case '''

    def tearDown (self):

        db.session.remove ()

        db.drop_all ()



    def test_avatar (self):

        u  = User (nickname='john', email='john@example.com')

        avatar = u.avatar (128)

# TODO might have to change the value to that of my gravatar
        expected = \
        'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'

        assert (avatar[0:len (expected)] == expected)
	
	

    def test_make_unique_nickname (self):

        u = User (nickname='john', email='john@example.com')

        db.session.add (u)

        db.session.commit()

        ''' Pass in the above USED nickname
        so what should be returned in john2 '''
        nickname = User.make_unique_nickname ('john')

        assert nickname != 'john'

        ''' Creating a new user with this non-used nickname '''
        u = User (nickname=nickname, email='susan@example.com')

        db.session.add (u)

        db.session.commit ()

        ''' Again, we pass in a name which is now USED
        expecting our method to return a unique variation 
        of this used nickname '''
        nickname2 = User.make_unique_nickname ('john')

        assert nickname2 != 'john'

        ''' nickname2 should be a variation on john2, so john3 
        And therefore, nickname2 != nickname '''
        assert nickname2 != nickname



    def test_follow (self):

        u1 = User (nickname='john', email='john@example.com')

        u2 = User (nickname='susan', email='susan@example.com')


        db.session.add (u1)

        db.session.add (u2)

        db.session.commit ()


        assert u1.unfollow (u2) is None # none because not following


        u = u1.follow (u2)  # u1 is following u2, returns u1

        db.session.add (u)  # u == u1

        db.session.commit ()


        assert u1.follow (u2) is None   # none because already following

        assert u1.is_following (u2)


        assert u1.followed.count () == 1

        assert u1.followed.first ().nickname == 'susan'


        assert u2.followers.count () == 1

        assert u2.followers.first ().nickname == 'john'


        u = u1.unfollow (u2)

        assert u is not None

# TESTING
        assert u == u1
# TESTING


        db.session.add (u)

        db.session.commit ()


        assert not u1.is_following (u2)

        assert u1.followed.count () == 0

        assert u2.followers.count () == 0

 

    def test_follow_posts (self):

        # make four users
        u1 = User (nickname='john', email='john@example.com')

        u2 = User (nickname='susan', email='susan@example.com')

        u3 = User (nickname='mary', email='mary@example.com')

        u4 = User (nickname='david', email='david@example.com')


        db.session.add (u1)

        db.session.add (u2)

        db.session.add (u3)

        db.session.add (u4)


        # make four posts

        utcnow = datetime.utcnow ()

        p1 = Post (body='post from john', author=u1, \
                   timestamp=utcnow + timedelta(seconds=1))

        p2 = Post (body='post from susan', author=u2, \
                   timestamp=utcnow + timedelta(seconds=2))

        p3 = Post (body='post from mary', author=u3, \
                   timestamp=utcnow + timedelta(seconds=3))

        p4 = Post (body='post from david', author=u4, \
                   timestamp=utcnow + timedelta(seconds=4))


        db.session.add (p1)

        db.session.add (p2)

        db.session.add (p3)

        db.session.add (p4)


        db.session.commit ()


        # setup the followers
        u1.follow (u1) # john follows himself 

        u1.follow (u2) # john follows susan

        u1.follow (u4) # john follows david


        u2.follow (u2) # susan follows herself

        u2.follow (u3) # susan follows marry


        u3.follow (u3) # mary follows herself

        u3.follow (u4) # mary follows david 


        u4.follow (u4) # david follows himself


        db.session.add (u1)

        db.session.add (u2)

        db.session.add (u3)

        db.session.add (u4)


        db.session.commit ()


        # check the followed posts of each user
        f1 = u1.followed_posts ().all ()

        f2 = u2.followed_posts ().all ()

        f3 = u3.followed_posts ().all ()

        f4 = u4.followed_posts ().all ()


        assert len (f1) == 3 # john  -- john, susan, david

        assert len (f2) == 2 # susan -- susan, mary

        assert len (f3) == 2 # mary  -- mary, david

        assert len (f4) == 1 # david -- david


        assert f1 == [p4, p2, p1] # because post four is the most recent

        assert f2 == [p3, p2]

        assert f3 == [p4, p3]

        assert f4 == [p4]


    def test_translation (self):

        assert microsoft_translate (u'English', 'en', 'es') == u'Inglés'

        assert microsoft_translate (u'Español', 'es', 'en') == u'Spanish'



if __name__ == '__main__':
    unittest.main()
