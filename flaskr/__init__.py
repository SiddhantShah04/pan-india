import os
from flask import Flask, jsonify, session
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from flask_mysqldb import MySQL
from datetime import timedelta
# A application factory function,which create a Flask instance


def create_app(test_config=None):
    # Create and config the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1400)
    CORS(app)

    api = Api(app, version='1.0', title='Sample API',
              description='A sample API')

    from . import auth
    api.add_namespace(auth.api)

    from . import client
    api.add_namespace(client.api)

    from . import image
    api.add_namespace(image.api)

    return app
