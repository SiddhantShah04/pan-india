from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog
from werkzeug.security import check_password_hash, generate_password_hash
import re
api = Namespace('auth', description='Apis for Pan Print India')

login = api.model('Login', {
    'email': fields.String(required=True, description='username', example="siddhantshah04@gmail.com"),
    'phone': fields.Integer(required=True, description='Phone number', example=1236547890),
    'password': fields.String(required=True, description='password'),
})

signup = api.model('Auth', {
    'email': fields.String(required=True, example="siddhantshah04@gmail.com"),
    'phone': fields.Integer(required=True, description='Phone number', example=1236547890),
    'password': fields.String(required=True, description='password'),
    'name': fields.String(required=True, description='Name'),
    'companyName': fields.String(required=True, description='Company Name'),
})


def checkEmail(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if(re.search(regex, email)):
        return(False)
    else:
        return(True)


@api.route('/login')
class Login(Resource):
    @api.doc('Enter your details')
    @api.expect(login)
    def post(self):
        '''Login for user'''

        try:
            db = get_db()
            cur = db.cursor()
            formData = api.payload
            email = formData['email']
            phone = str(formData["phone"])
            if(len(phone) != 10):

                return({"message": 'Invalid phone number'}, 400)
            if(checkEmail(email)):
                abort(400, {'error': 'Invalid email address'})
            password = formData['password']
            sql = "SELECT * FROM users WHERE email=%s"
            data = (email,)
            cur.execute(sql, data)

            user = cur.fetchone()
            print(user)
            error = None
            if user is None:

                return({"status": False, "information": "Incorrect Email.", "error_code": "401", "error_message": "Incorrect Email."}, 401)
            elif not check_password_hash(str(user['password']), password):

                return({"status": False, "information": "Incorrect password.", "error_code": "401", "error_message": "Incorrect password."}, 401)

            else:
                session.clear()
                session['user_id'] = user['id']
                activityLog.activity(
                    user['id'], "user", f"user With id {user['id']} logged in", "Login")
            return({"status": True, "information": "The Client has been loggedin", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()


@api.route('/logout')
class Logout(Resource):
    @api.doc('Logout')
    def get(self):
        '''Logout for user'''

        activityLog.activity(
            session['user_id'], "user", f"user With id {session['user_id']} logged out.", "Logout")
        session.pop('user_id', None)
        return({"status": True, "information": 'You successfully logged out', "error_code": "", "error_message": ""}, 201)


@api.route('/signup')
@api.response(404, 'Url not found')
class Signup(Resource):
    @api.doc('Signup')
    @api.expect(signup)
    # @api.marshal_with(signup)
    def post(self):
        '''Signup for user'''
        try:
            db = get_db()
            cur = db.cursor()

            formData = api.payload
            name = formData['name']
            password = formData['password']
            email = formData['email']
            phone = str(formData['phone'])
            companyName = str(formData['companyName'])
            if(len(phone) != 10):
                return({"status": False, "information": "Invalid phone number'", "error_code": "401", "error_message": "Invalid phone number"}, 401)
            if(checkEmail(email)):
                return({"status": False, "information": "Invalid email.'", "error_code": "401", "error_message": "Invalid email."}, 401)

            error = None

            sql = "SELECT * FROM users WHERE email=%s"
            data = (email,)
            cur.execute(sql, data)

            if(cur.fetchone()):
                return({"status": False, "information": "User is already exists.", "error_code": "500", "error_message": "User is already exists."}, 401)

            else:
                sql = "SELECT * FROM clientConfiguration WHERE companyName=%s"
                data = (companyName,)
                cur.execute(sql, data)
                clientDetails = cur.fetchone()
                if(clientDetails):

                    cur.execute("INSERT INTO users(companyName,email,name,password,phone,clientId) VALUES (%s,%s,%s,%s,%s,%s)", (
                        companyName, email, name, generate_password_hash(str(password)), phone, clientDetails['clientId']))

                    activityLog.activity(
                        0, "user", f"user With id {email} account  created.", "signup")
                    db.commit()
                else:
                    return({"status": False, "information": "Company name does not exists.", "error_code": "500", "error_message": "Company name does not exists."}, 401)

                return({"status": True, "information": "User account sucessfully created.", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()


# Registers a function that runs before the view function, no matter what URL is requested.

# {
#   "email": "siddhant044@gmail.com",
#   "phone": 0,
#   "password": "string",
#   "name": "string"
# }


# @api.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if(user_id is None):
#         g.user = None
#     else:
#         g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return ('unauthorized')

        return view(**kwargs)

    return
