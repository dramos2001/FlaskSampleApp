import sqlite3
from datetime import datetime

import click
from flask import current_app, g


# called when the app is created and is handling a request
def getDb():
    if 'db' not in g:
        # establishes a connection to the file pointed by db config key
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # tell the connection to return rows that behave like dictionaries
        g.db.row_factory = sqlite3.Row
        
    return g.db

# close the database if a connection was created
def closeDb(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        
def initDb():
    db = getDb()
    
    # open a file relative to flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# command that calls initdb func and shows success message
@click.command('init-db')
def initDbCommand():
    # clear existing data and create new tables
    initDb()
    click.echo('Initialized the database.')
    
def initApp(app):
    app.teardown_appcontext(closeDb)  # call when cleaning up after returning response
    app.cli.add_command(initDbCommand) # add new command that can be called with 'flask' command

# tells Python how to interpret timestamp values in db
sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))