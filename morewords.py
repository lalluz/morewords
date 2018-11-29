from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import flash
from flask import jsonify
from flask import session as login_session
from flask import abort
from flask import make_response

from flask_wtf.csrf import CSRFProtect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, Language, Word

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import httplib2
import json
import requests


app = Flask(__name__)

engine = create_engine('postgresql+psycopg2://vagrant:wlapaella@localhost:5432/morewords')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

csrf = CSRFProtect(app)


@app.route('/')
@app.route('/vocabulary/', methods=['GET'])
def vocabulary():
    """Return the main page with all languages and latest words."""
    languages = session.query(Language).order_by('name').all()
    latest_words = session.query(Word).order_by('id desc').limit(10)
    is_user_logged_in = True if 'username' in login_session else False

    context = {'languages': languages,
               'latest_words': latest_words,
               'is_user_logged_in': is_user_logged_in}

    return render_template('vocabulary.html', **context)


@app.route('/vocabulary/languages', methods=['GET'])
def language_list():
    """Return the page to manage all languages."""
    languages = session.query(Language).order_by('name').all()
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in:
        user = session.query(User).filter_by(id=login_session['user_id']).one()
    else:
        user = None

    context = {'languages': languages,
               'is_user_logged_in': is_user_logged_in,
               'user': user}

    return render_template('language_list.html', **context)


@app.route('/vocabulary/language/add/', methods=['GET', 'POST'])
def language_add():
    """Return the page to add a language."""
    is_user_logged_in = True if 'username' in login_session else False
    context = {'is_user_logged_in': is_user_logged_in}

    if request.method == 'POST':
        if not is_user_logged_in:
            flash('You have to log in to add a language.')

            return render_template('language_add.html', **context)

        new_language = Language(name=request.form['name'].lower(),
                                user_id=login_session['user_id'])
        session.add(new_language)
        session.commit()
        flash("New Language Created!")

        return redirect(url_for('vocabulary'))

    else:
        if not is_user_logged_in:
            flash('You have to log in to add a language.')

        return render_template('language_add.html', **context)


@app.route('/vocabulary/<int:language_id>/edit/', methods=['GET', 'POST'])
def language_edit(language_id):
    """Return the page to edit the given language."""
    to_edit = session.query(Language).filter_by(id=language_id).one()
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in and to_edit.user_id == login_session['user_id']:
        is_user_authorized = True
    else:
        is_user_authorized = False
    no_permission_msg = ('Sorry, you don\'t have permission '
                         'to edit this language.')

    context = {'to_edit': to_edit,
               'is_user_authorized': is_user_authorized,
               'is_user_logged_in': is_user_logged_in}

    if request.method == 'POST':
        if not is_user_authorized:
            flash(no_permission_msg)

            return render_template('language_edit.html', **context)

        to_edit.name = request.form['name'].lower()
        session.add(to_edit)
        session.commit()
        flash("Language Saved!")

        return redirect(url_for('vocabulary'))

    else:
        if not is_user_authorized:
            flash(no_permission_msg)

        return render_template('language_edit.html', **context)


@app.route('/vocabulary/<int:language_id>/delete/', methods=['GET', 'POST'])
def language_delete(language_id):
    """Return the page to delete the given language."""
    to_delete = session.query(Language).filter_by(id=language_id).one()
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in and to_delete.user_id == login_session['user_id']:
        is_user_authorized = True
    else:
        is_user_authorized = False
    message = 'Sorry, you don\'t have permission to delete this language.'

    context = {'to_delete': to_delete,
               'is_user_authorized': is_user_authorized,
               'is_user_logged_in': is_user_logged_in}

    if request.method == 'POST':
        if not is_user_authorized:
            flash(message)

            return render_template('language_delete.html', **context)

        words = session.query(Word).filter_by(language_id=language_id).count()
        if words > 0:
            flash('Sorry, there are words saved in this language, '
                  'you can\'t delete it.')

            return redirect(url_for('vocabulary'))

        session.delete(to_delete)
        session.commit()
        flash("Language Deleted!")

        return redirect(url_for('vocabulary'))

    else:
        if not is_user_authorized:
            flash(message)

        return render_template('language_delete.html', **context)


@app.route('/vocabulary/<int:language_id>/words/', methods=['GET'])
def word_list(language_id):
    """Return the page with all words in the given language."""
    language = session.query(Language).filter_by(id=language_id).one()
    words = (session.query(Word).filter_by(language_id=language_id).
             order_by('name').all())
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in:
        user = session.query(User).filter_by(id=login_session['user_id']).one()
    else:
        user = None

    context = {'language': language,
               'words': words,
               'is_user_logged_in': is_user_logged_in,
               'user': user}

    return render_template('word_list.html', **context)


@app.route('/vocabulary/<int:language_id>/<int:word_id>/', methods=['GET'])
def word_detail(language_id, word_id):
    """Return the detail page of the given word."""
    word = session.query(Word).filter_by(id=word_id).one()
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in:
        user = session.query(User).filter_by(id=login_session['user_id']).one()
    else:
        user = None

    context = {'word': word,
               'is_user_logged_in': is_user_logged_in,
               'user': user}

    return render_template('word_detail.html', **context)


@app.route('/vocabulary/word/add/', methods=['GET', 'POST'])
def word_add(language_id=None):
    """Return the page to add a word."""
    languages = session.query(Language).all()
    is_user_logged_in = True if 'username' in login_session else False
    if len(languages) == 0:
        flash('You should add a language first.')

        return redirect(url_for('vocabulary'))

    if request.method == 'POST':
        language_id = request.form['language']
        language = session.query(Language).filter_by(id=language_id).one()

        new_word = Word(name=request.form['name'].lower(),
                        translation=request.form['translation'],
                        notes=request.form['notes'],
                        language=language,
                        user_id=login_session['user_id'])
        session.add(new_word)
        session.commit()
        flash("New Word Created!")

        return redirect(url_for('word_list', language_id=language.id))

    else:
        context = {'languages': languages,
                   'is_user_logged_in': is_user_logged_in}

        return render_template('word_add.html', **context)


@app.route('/vocabulary/<int:language_id>/<int:word_id>/edit/',
           methods=['GET', 'POST'])
def word_edit(language_id, word_id):
    """Return the page to edit the given word."""
    languages = session.query(Language).all()
    language = session.query(Language).filter_by(id=language_id).one()
    to_edit = session.query(Word).filter_by(id=word_id).one()
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in and to_edit.user_id == login_session['user_id']:
        is_user_authorized = True
    else:
        is_user_authorized = False
    no_permission_msg = 'Sorry, you don\'t have permission to edit this word.'

    context = {'languages': languages,
               'language': language,
               'to_edit': to_edit,
               'is_user_authorized': is_user_authorized,
               'is_user_logged_in': is_user_logged_in}

    if request.method == 'POST':
        if not is_user_authorized:
            flash(no_permission_msg)

            return render_template('word_edit.html', **context)

        to_edit.name = request.form['name'].lower()
        to_edit.translation = request.form['translation']
        to_edit.notes = request.form['notes']
        if request.form.get('is_learned'):
            to_edit.is_learned = True
        else:
            to_edit.is_learned = False
        session.add(to_edit)
        session.commit()
        flash("Word Saved!")
        context = {'language_id': language.id,
                   'word_id': to_edit.id}

        return redirect(url_for('word_detail', **context))

    else:
        if not is_user_authorized:
            flash(no_permission_msg)

        return render_template('word_edit.html', **context)


@app.route('/vocabulary/<int:language_id>/<int:word_id>/delete/',
           methods=['GET', 'POST'])
def word_delete(language_id, word_id):
    """Return the page to delete the given word."""
    language = session.query(Language).filter_by(id=language_id).one()
    to_delete = session.query(Word).filter_by(id=word_id).one()
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in and to_delete.user_id == login_session['user_id']:
        is_user_authorized = True
    else:
        is_user_authorized = False
    no_permission_msg = ('Sorry, you don\'t have permission '
                         'to delete this word.')

    context = {'to_delete': to_delete,
               'is_user_authorized': is_user_authorized,
               'is_user_logged_in': is_user_logged_in}

    if request.method == 'POST':
        if not is_user_authorized:
            flash(no_permission_msg)

            return render_template('word_delete.html', **context)

        session.delete(to_delete)
        session.commit()
        flash("Word Deleted!")

        return redirect(url_for('word_list', language_id=language_id))
    else:
        if not is_user_authorized:
            flash(no_permission_msg)

        return render_template('word_delete.html', **context)


# List of user words to learn
@app.route('/vocabulary/<int:language_id>/<int:user_id>/review',
           methods=['GET'])
def personal_review(user_id, language_id):
    """Return a page with all words with is_learned==False."""
    language = session.query(Language).filter_by(id=language_id).one()
    words = session.query(Word).filter_by(language_id=language_id,
                                          user_id=user_id,
                                          is_learned=False)
    is_user_logged_in = True if 'username' in login_session else False
    if is_user_logged_in and user_id == login_session['user_id']:
        is_user_authorized = True
    else:
        is_user_authorized = False

    context = {'is_user_authorized': is_user_authorized,
               'is_user_logged_in': is_user_logged_in,
               'language': language,
               'words': words}
    if not is_user_authorized:
        flash('Sorry, you don\'t have permission to see this page.')

    return render_template('personal_review.html', **context)


# SIGNUP, LOGIN AND LOGOUT
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Return the page to sign up without using Google or Facebook."""
    is_user_logged_in = True if 'username' in login_session else False
    context = {'is_user_logged_in': is_user_logged_in}

    if request.method == 'POST':
        new_user = User(username=request.form['username'],
                        email=request.form['email'],
                        picture=None)
        new_user.hash_password(request.form['password'])
        session.add(new_user)
        session.commit()

        languages = session.query(Language).order_by('name').all()
        latest_words = session.query(Word).order_by('id desc').limit(10)
        context = {'languages': languages,
                   'latest_words': latest_words,
                   'is_user_logged_in': is_user_logged_in}
        flash('Hi %s, you have successfully registered.' % new_user.username)
        flash('Log in to use morewords.')

        return render_template('vocabulary.html', **context)

    return render_template('signup.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Return the page with all login options."""
    is_user_logged_in = True if 'username' in login_session else False
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    context = {'is_user_logged_in': is_user_logged_in,
               'STATE': state}

    if request.method == 'POST':
        user_email = request.form['email']
        user_id = get_user_id(user_email)
        user_password = request.form['password']
        if user_id:
            user = session.query(User).filter_by(id=user_id).one()
            if user.verify_password(user_password):
                login_session['user_id'] = user.id
                login_session['username'] = user.username
                login_session['email'] = user.email
                login_session['picture'] = None
                login_session['provider'] = 'morewords'
                is_user_logged_in = True

                languages = session.query(Language).order_by('name').all()
                latest_words = (session.query(Word).order_by('id desc').
                                limit(10))
                context = {'languages': languages,
                           'latest_words': latest_words,
                           'is_user_logged_in': is_user_logged_in}
                flash('Hello %s!' % user.username)

                return render_template('vocabulary.html', **context)

        flash('Email or password incorrect. Try again.')

    return render_template('login.html', **context)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connect with Google OAuth service to login a Google user."""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = (make_response(
                    json.dumps('Failed to upgrade the authorization code.'),
                    401))
        response.headers['Content-Type'] = 'application/json'

        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = (make_response(
                    json.dumps("Token's user ID doesn't match given user ID."),
                    401))
        response.headers['Content-Type'] = 'application/json'

        return response

    # Verify that the access token is valid for this app.
    CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
    if result['issued_to'] != CLIENT_ID:
        response = (make_response(
                    json.dumps("Token's client ID does not match app's."),
                    401))
        response.headers['Content-Type'] = 'application/json'

        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = (make_response(
                    json.dumps('Current user is already connected.'), 200))
        response.headers['Content-Type'] = 'application/json'

        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if not make a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash("Hello %s!" % login_session['username'])

    return str(login_session)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Connect with Facebook OAuth service to login a Facebook user."""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    access_token = request.data
    app_id = (json.loads(open('fb_client_secrets.json', 'r').
              read())['web']['app_id'])
    app_secret = (json.loads(
                  open('fb_client_secrets.json', 'r').
                  read())['web']['app_secret'])
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # nopep8
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server
        token exchange we have to split the token first on
        commas and select the first index which gives us the
        key : value for the server access token then we split
        it on colons to pull out the actual token value and
        replace the remaining quotes with nothing so that
        it can be used directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    # Get user data
    url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token  # nopep8
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # nopep8
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # See if user exists, if not make a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash("Hello %s!" % login_session['username'])

    return str(login_session)


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnect a Google user."""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = (make_response(
                    json.dumps('Current user not connected.'), 401))
        response.headers['Content-Type'] = 'application/json'

        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = (make_response(
                    json.dumps('Successfully disconnected.'), 200))
        response.headers['Content-Type'] = 'application/json'

        return response

    else:
        response = (make_response(
                    json.dumps('Failed to revoke token for given user.'), 400))
        response.headers['Content-Type'] = 'application/json'

        return response


# Facebook disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnect a Facebook user."""
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s' %
           (facebook_id, access_token))
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]

    return


@app.route('/disconnect')
def disconnect():
    """Disconnect users based on provider."""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")

        return redirect(url_for('vocabulary'))

    else:
        flash("You were not logged in")

        return redirect(url_for('vocabulary'))


# API Endpoint
@app.route('/api/v0/vocabulary', methods=['GET'])
def vocabulary_json():
    """List all words grouped by language."""
    languages = session.query(Language).all()
    serialized_languages = [l.serialize for l in languages]

    for i in range(len(serialized_languages)):
        words = (session.query(Word).
                 filter_by(language_id=serialized_languages[i]["id"]).all())
        serialized_words = [w.serialize for w in words]
        serialized_languages[i]["Words"] = serialized_words

    return jsonify(Vocabulary=serialized_languages)


@app.route('/api/v0/languages', methods=['GET'])
def language_list_json():
    """List all languages."""
    languages = session.query(Language).all()

    return jsonify(Languages=[l.serialize for l in languages])


@app.route('/api/v0/words', methods=['GET'])
def word_list_json():
    """List all words."""
    words = session.query(Word).all()

    return jsonify(Words=[w.serialize for w in words])


@app.route('/api/v0/languages/<string:language_name>/words', methods=['GET'])
def language_word_list_json(language_name):
    """List all words in the given language."""
    language = session.query(Language).filter_by(name=language_name).one()
    words = session.query(Word).filter_by(language_id=language.id)

    return jsonify(Words=[w.serialize for w in words])


@app.route('/api/v0/languages/<string:language_name>/words/<string:word_name>',
           methods=['GET'])
def language_word_json(language_name, word_name):
    """List all entries for a given word in the given language."""
    language = session.query(Language).filter_by(name=language_name).one()
    word_query = session.query(Word).filter_by(language_id=language.id,
                                               name=word_name)

    return jsonify(Word=[w.serialize for w in word_query])


@app.route('/api/v0/words/<string:word_name>', methods=['GET'])
def word_json(word_name):
    """List all entries for the given word in any language."""
    word_query = session.query(Word).filter_by(name=word_name)

    return jsonify(Word=[w.serialize for w in word_query])


def create_user(login_session):
    """Helper function that creates a user."""
    new_user = User(username=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


def get_user_id(email):
    """Helper function that retrieves a user id from the given email."""
    try:
        user = session.query(User).filter_by(email=email).one()

        return user.id

    except NoResultFound:
        return None


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
