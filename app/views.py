from flask import render_template, flash, \
        redirect, session, url_for, request, g

from flask_login import login_user, logout_user, current_user, login_required

from datetime import datetime

from app import app, db, lm, oid    # lm == login_manager, oid == open_id

from .forms import LoginForm, EditForm

from .models import User


''' in login view function we check g.user to determine if user is already 
logged in -- we use before_request event from Flask to initialize this. 
Any functions that are decorated with before_request will run before the view
function -- each time a request is received '''
@app.before_request
def before_request ():

    ''' current_user global set by Flask-login -- we put a copy in the g
    object to have better access to it! With this, all requests will
    have access to the logged in user, even inside templates '''
    g.user = current_user 


    if g.user.is_authenticated:

        g.user.last_seen = datetime.utcnow ()

        db.session.add (g.user)

        db.session.commit ()


@lm.user_loader
def load_user (id):

    return User.query.get (int (id))


''' Home Page '''

@app.route ('/')
@app.route ('/index')
@login_required     # send !logged-in user to login view if trying to access
def index():

    user = g.user 

    posts = [ # fake array of posts
        {
            'author': {'nickname': 'John-Luke'},
            'body': 'Beautiful Bunny Bun-Buns!'
        },
        {
            'author': {'nickname': 'Snek'},
            'body': 'Green Garbage'
        },
        {
            'author': {'nickname': 'Frampton'},
            'body': 'Whomany woman get leks?'
        },
        {
            'author': {'nickname': 'Shappard'},
            'body': 'I think you mean Sheppard'
        },
        {
            'author': {'nickname': 'Bloody Joe'},
            'body': 'All that hath wraughtfully scorn'
        }
    ]
# TESTING
    
    return render_template ('index.html', 
                           title = 'Home', 
                           user = user,
                           posts = posts
                           )



''' Login Page '''

@app.route ('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login ():
    
    ''' g is global object setup by flask
    it will hold the instance of user -- so, this check prevents
    the user from seeing the login page a second time '''
    if g.user is not None and g.user.is_authenticated:

        return redirect (url_for ('index'))

    
    form = LoginForm ()     # object instance of class in app/forms.py


    if form.validate_on_submit ():

        ''' store the result of remember_me boolean inside flask.session
        which, unlike flask.g which only lasts for life of request, session
        remains for all requests made by the same client '''
        session['remember_me'] = form.remember_me.data

        return oid.try_login (form.openid.data, ask_for=['nickname', 'email'])


    return render_template('login.html',
                          title = 'Sign In',
                          form = form,
                          providers = app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login (response):

    if response.email is None or response.email == '':

        flash ('Invalid login, Please try again.')

        return redirect (url_for ('login'))


    user = User.query.filter_by (email= response.email).first ()


    ''' This user has just been created; not in the database '''
    if user is None:

        nickname = response.nickname


        if nickname is None or nickname == '':

            nickname = response.email.split('@')[0]


        nickname = User.make_unique_nickname (nickname)

        user = User(nickname=nickname, email=response.email)


        db.session.add (user)

        db.session.commit ()


    remember_me = False         # why is this hard coded?


    if 'remember_me' in session:

        remember_me = session['remember_me']

        session.pop ('remember_me', None)


    ''' Flask-login login_user () function '''
    login_user (user, remember = remember_me)


    ''' If the user was trying to access a page that required login,
    they were redirected to the login view, and are now here
    We saved the page they were trying to access in Flask's `next`
    so we can return them back where they came from, otherwise, home '''
    return redirect (request.args.get ('next') or url_for ('index'))


''' Logout View '''

@app.route ('/logout')
def logout ():

    logout_user ()

    return redirect (url_for ('index'))


''' User Profile View '''

''' <nickname> is an argument -- translates into an argument of the same name
added to the view. When the client requests, say URI /user/miguel the view
function will be invoked with `nickname` set to 'miguel' '''
@app.route ('/user/<nickname>')     
@login_required
def user (nickname):

    user = User.query.filter_by (nickname = nickname).first ()


    if user == None:

        flash ('User %s not found.' % nickname)

        return redirect (url_for ('index'))


    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]

    
    return render_template ('user.html',
                           user = user,
                           posts = posts)



''' Edit Profile Page '''

@app.route ('/edit', methods = ['GET', 'POST'])
@login_required
def edit ():

    form = EditForm (g.user.nickname) # supply original_nickname to form


    if form.validate_on_submit ():

        g.user.nickname = form.nickname.data

        g.user.about_me = form.about_me.data


        db.session.add (g.user)

        db.session.commit ()


        flash ('Your changes have been saved.')


        return redirect (url_for ('edit'))

    else:

        form.nickname.data = g.user.nickname

        form.about_me.data = g.user.about_me


    return render_template ('edit.html', form = form)



''' Custom Error Handling '''
@app.errorhandler (404)
def not_found_error (error):

    return render_template ('404.html'), 404


@app.errorhandler (500)
def internal_error (error):

    ''' This is necessary because this function 
    will be called as a result of an exception
    If the exception was triggered by a database error 
    then the database session is going to arrive 
    in an invalid state, so we have to roll it back in 
    case a working session is needed for the rendering 
    of the template for the 500 error. '''
    db.session.rollback ()

    return render_template ('500.html'), 500
