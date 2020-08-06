import sqlite3
from os import path
import flask
from flask import Flask, request, g
from flask_login import LoginManager, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = '9d9da5d5d4dfa53f5e10a600'

DATABASE = 'database.db'
SCHEMA = 'schema.sql'
RETRIEVE_URL = 'http://127.0.0.1:5000/retrieve/{}'

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')

def init_db():
    # TODO: Change this to checking if table exists
    if path.exists(DATABASE):
        return
    with app.app_context():
        db = get_db()
        with app.open_resource(SCHEMA, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def write_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(somewhere)

@app.route("/test", methods=['GET'])
@login_required
def test_login():
    return "Login works"

@app.route('/retrieve/<int:paste_id>', methods=['GET'])
def retrieve(paste_id):
    text = query_db('select * from pastes where paste_id = ?', [paste_id], one=True)
    if text is None:
        return { 'text': "No Post exists"}
    return { 'text': text[1] }

@app.route('/write/<string:text>', methods=['POST'])
def write(text):
    paste_id = write_db('insert into pastes (text) values (?);', [text])
    return "See value at: " + RETRIEVE_URL.format(paste_id)

### Start up Tasks

init_db()

### End Startup Tasks

