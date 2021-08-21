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
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config['MAIL_SERVER'] = environ.get("MAIL_SERVER")
    app.config['MAIL_PORT'] = environ.get("MAIL_PORT")
    app.config['MAIL_USERNAME'] = environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = environ.get("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = environ.get("MAIL_USE_TLS")
    app.config['MAIL_USE_SSL'] = environ.get("MAIL_USE_SSL")

    # @app.before_request
    # def before_request():
    #     client = request.host.split('.')
    #     app.config['SERVER_NAME'] = f"{client[0]}.localhost:5000"

    api = Api(app, version='1.0', title='Sample API',
              description='A sample API')

    from . import auth
    api.add_namespace(auth.api)

    from . import client
    api.add_namespace(client.api)

    from . import image
    api.add_namespace(image.api)

    from . import users
    api.add_namespace(users.api)

    from . import order
    api.add_namespace(order.api)

    from . import product
    api.add_namespace(product.api)
    return app
