from flask import render_template, flash, \
        redirect, session, url_for, request, g

from flask import jsonify

from flask_login import login_user, logout_user, current_user, login_required

from flask_babel import gettext

from datetime import datetime

# lm == login_manager, oid == open_id
from app import app, db, lm, oid, babel

from .forms import LoginForm, EditForm, PostForm, SearchForm

from .models import User, Post

from .emails import follower_notification

from .translate import microsoft_translate

from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS

from config import LANGUAGES

from guess_language import guessLanguage



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

        g.search_form = SearchForm ()
    
    ''' expose the language code of the user '''
    g.locale = get_locale ()


@lm.user_loader
def load_user (id):

    return User.query.get (int (id))


''' Home Page '''

@app.route ('/', methods=['GET', 'POST'])
@app.route ('/index', methods=['GET', 'POST'])
@app.route ('/index/<int:page>', methods=['GET', 'POST'])
@login_required     # send !logged-in user to login view if trying to access
def index(page=1):

    form = PostForm () 

    if form.validate_on_submit ():
        
        language = guessLanguage (form.post.data)

        if language == 'UNKNOWN' or len(language) > 5:

            language = ''
        
        post = Post (body=form.post.data, timestamp=datetime.utcnow (),
                     author=g.user, language = language)

        db.session.add (post)

        db.session.commit ()

        flash (gettext('Your post is now live!'))

        return redirect (url_for ('index'))


    posts = g.user.followed_posts ().paginate (
        page, POSTS_PER_PAGE, False)


    return render_template ('index.html', 
                           title = 'Home', 
                           form=form,
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

        flash (gettext('Invalid login, Please try again.'))

        return redirect (url_for ('login'))


    user = User.query.filter_by (email= response.email).first ()


    ''' This user has just been created; not in the database '''
    if user is None:

        nickname = response.nickname


        if nickname is None or nickname == '':

            nickname = response.email.split('@')[0]

        ''' Call make_valid_nickname() to remove all non-valid characters '''
        nickname = User.make_valid_nickname (nickname)

        nickname = User.make_unique_nickname (nickname)

        user = User(nickname=nickname, email=response.email)


        db.session.add (user)

        db.session.commit ()

        # make the user follow themself
        db.session.add (user.follow(user))

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
@app.route ('/user/<nickname>/<int:page>')     
@login_required
def user (nickname, page=1):

    user = User.query.filter_by (nickname = nickname).first ()


    if user == None:

        flash (gettext('User %(nickname)s not found.', nickname = nickname))

        return redirect (url_for ('index'))


    posts = user.posts.paginate (page, POSTS_PER_PAGE, False) 

    
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


        flash (gettext('Your changes have been saved.'))


        return redirect (url_for ('edit'))

    else:

        form.nickname.data = g.user.nickname

        form.about_me.data = g.user.about_me


    return render_template ('edit.html', form = form)


@app.route ('/follow/<nickname>')
@login_required
def follow (nickname):

    user = User.query.filter_by (nickname=nickname).first ()

    if user is None:

        flash ('User %s not found.' % nickname)

        return redirect (url_for ('index'))


    if user == g.user:

        flash (gettext('You can\'t follow yourself!'))

        return redirect (url_for ('index'))


    u = g.user.follow(user)

    if u is None:

        flash (gettext('Cannot follow %(nickname)s.', nickname = nickname))

        return redirect (url_for ('user', nickname=nickname))


    db.session.add (u)

    db.session.commit ()


    follower_notification (user, g.user)    # send email


    flash (gettext('You are now following %(nickname)s!', nickname = nickname))

    return redirect (url_for ('user', nickname=nickname))




@app.route ('/unfollow/<nickname>')
@login_required
def unfollow (nickname):

    user = User.query.filter_by (nickname=nickname).first ()

    if user is None:

        flash ('User %s not found.' % nickname)

        return redirect (url_for ('index'))


    if user == g.user:

        flash (gettext('You can\'t unfollow yourself!'))

        return redirect (url_for ('index'))


    u = g.user.unfollow(user)

    if u is None:

        flash (gettext('Cannot unfollow %(nickname)s.', nickname = nickname))

        return redirect (url_for ('user', nickname=nickname))


    db.session.add (u)

    db.session.commit ()

    flash (gettext(
        'You have stopped following %(nickname)s.', nickname = nickname))

    return redirect (url_for ('user', nickname=nickname))


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


''' This function doesn't really do much -- just collects the search data
and redirects to another page, passing this query as an argument
The reason that the work isn't done here is in case a user hits the refresh
page -- the form data would have to be resubmitted
This is avoided when the response to a POST request is a redirect -- because
after the redirect the browser's refresh will reload the redirected page '''
@app.route ('/search', methods=['POST'])
@login_required
def search ():

    if not g.search_form.validate_on_submit ():

        return redirect (url_for ('index'))

    return redirect (url_for ('search_results', \
                              query=g.search_form.search.data))



@app.route ('/search_results/<query>')
@login_required
def search_results (query):

    results = Post.query.whoosh_search (query, MAX_SEARCH_RESULTS).all ()

    return render_template ('search_results.html',
                           query=query,
                           results=results)



@app.route ('/translate', methods=['POST'])
@login_required
def translate ():

    return jsonify({
        'text': microsoft_translate(
            request.form['text'],
            request.form['sourceLang'],
            request.form['destLang']) })



@babel.localeselector
def get_locale ():

    return 'es' #return request.accept_languages.best_match (LANGUAGES.keys ())
