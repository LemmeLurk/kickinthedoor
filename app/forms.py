from flask_wtf import Form

from wtforms import StringField, BooleanField, TextAreaField

from wtforms.validators import DataRequired, Length

from app.models import User


class LoginForm (Form):

    # Input field with validation requiring input
    openid = StringField ('openid', validators = [DataRequired ()])

    remember_me = BooleanField ('remember_me', default = False)


class EditForm (Form):

    nickname = StringField ('nickname', validators = [DataRequired ()])

    about_me = TextAreaField (
        'about_me', validators = [Length(min = 0, max = 140)])



    ''' Takes `original_nickname` to determine if the nickname has
    changed or not -- this is done by the validate() method
    If it hasn't changed, then it accepts it, otherwise, then it makes
    sure the new nickname does not exist in the database.
    This works because there is a check in the view when creating the account
    that will make sure that this `original_name` is unique '''
    def __init__ (self, original_nickname, *args, **kwargs):

        Form.__init__ (self, *args, **kwargs)

        self.original_nickname = original_nickname



    def validate (self):

        if not Form.validate (self):

            return False

        ''' As explained above, the value of original_nickname is set
        when this object was created, so it contains the name before being
        modified '''
        if self.nickname.data == self.original_nickname:
            
            return True


        ''' If another user has this nickname, user will != None '''
        user = User.query.filter_by (nickname=self.nickname.data).first()


        if user != None:

            self.nickname.errors.append (
                'This nickname is already in use. Please choose another one.')

            return False


        return True
