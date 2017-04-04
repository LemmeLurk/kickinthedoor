#!flask/bin/python

import os

import unittest


from config import basedir

from app import app, db

from app.models import User



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


        db.session.add (u)

        db.session.commit ()


        assert not u1.is_following(u2)

        assert u1.followed.count () == 0

        assert u2.followers.count () == 0



if __name__ == '__main__':
    unittest.main()
