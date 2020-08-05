import sqlite3
from os import path
from flask import Flask, request, g
app = Flask(__name__)

DATABASE = 'database.db'
SCHEMA = 'schema.sql'
RETRIEVE_URL = 'http://127.0.0.1:5000/retrieve/{}'

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

