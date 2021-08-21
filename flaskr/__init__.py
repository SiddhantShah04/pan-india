import os
from flask import Flask, jsonify, session, request
from flask_restx import Resource, Api, fields
from flask_cors import CORS

from flask_mysqldb import MySQL
from datetime import timedelta
from os import environ


# A application factory function,which create a Flask instance


def create_app(test_config=None):
    # Create and config the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    # app.config['SERVER_NAME'] = "xyz.localhost:5000"
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1400)
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    api = Api(app, version='1.0', title='Sample API',
              description='A sample API')

    @api.route('/')
    class HelloWorld(Resource):
        def get(self):
            return("ghj")

    return app
