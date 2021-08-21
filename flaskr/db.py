import sqlite3
import click
import psycopg2
import MySQLdb

import MySQLdb.cursors
# g is a special object that is unique for each request.
# It is used to store data that might be accessed by multiple functions during the request.
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if('db' not in g):
        # current_app is another special object that points to the Flask application handling the request.
        g.db = MySQLdb.connect(database="printpanindia", user="print_pan", password="print@!9@8",
                               host="printpanindia.com", cursorclass=MySQLdb.cursors.DictCursor)

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if(db is not None):
        db.close()


def init_db():
    db = get_db()
    curr = db.cursor()
    with current_app.open_resource('schema.sql') as f:
        curr.execute(f.read().decode('utf8'))

    # defines a command line command called init-db that calls the init_db function


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# A takes an application and does the registration,with the application instance


def init_app(app):

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
