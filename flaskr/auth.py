from logging import log
from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog
from werkzeug.security import check_password_hash, generate_password_hash
import re
from flaskr.util.sendOtp import sendMessgae
from random import randint
from time import time
api = Namespace('auth', description='Apis for Pan Print India')

login = api.model('Login', {
    'email': fields.String(required=True, description='username', example="siddhantshah04@gmail.com"),
    'phone': fields.Integer(required=True, description='Phone number', example=8828286463),
    'password': fields.String(required=True, description='password'),
})

signup = api.model('signup', {
    'email': fields.String(required=True, example="siddhantshah04@gmail.com"),
    'phone': fields.Integer(required=True, description='Phone number', example=8828286463),
    'password': fields.String(required=True, description='password'),
    'name': fields.String(required=True, description='Name'),
    'companyName': fields.String(required=True, description='Company Name'),
    'otp': fields.Integer(required=True, description='OTP', min=6),

})

ChangePassword = api.model('ChangePassword', {
    'currentPassword': fields.String(required=True,  description='password'),
    'newPassword': fields.String(required=True,  description='password'),
    'confirmPassword': fields.String(required=True, description='password'),
})
SendOtp = api.model('SendOtp', {
    'phone': fields.Integer(required=True, description='Phone number', example=8828286463),

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
            otp = formData['otp']

            email = formData['email']
            phone = str(formData['phone'])
            companyName = str(formData['companyName'])
            if(len(phone) != 10):
                return({"status": False, "information": "Invalid phone number'", "error_code": "401", "error_message": "Invalid phone number"}, 401)
            if(checkEmail(email)):
                return({"status": False, "information": "Invalid email.'", "error_code": "401", "error_message": "Invalid email."}, 401)

            if(session.get('otp') == None or otp != session['otp'] or int(time()) > session["setTimeOut"]+300000):

                return({"status": False, "information": "Invalid OTP.", "error_code": "400", "error_message": "Invalid OTP."}, 400)
            session.pop('otp')
            session.pop('setTimeOut')

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


@api.route('/sendOtp')
@api.response(404, 'Url not found')
class SendOtp(Resource):
    @api.doc('sendOtp')
    @api.expect(SendOtp)
    def post(self):
        try:
            db = get_db()
            cur = db.cursor()

            formData = api.payload
            phone = str(formData['phone'])

            if(len(phone) != 10):

                return({"status": False, "information": "Invalid phone number.", "error_code": "401", "error_message": "Invalid phone number"}, 401)
            otp = randint(100000, 999999)
            session['otp'] = otp
            session["setTimeOut"] = int(time())
            message = f"{otp} is your Print Pan India Verification code. Valid for 5 minutes."
            phone = "+91"+phone
            resp = sendMessgae(phone, message)

            return({"status": True, "information": "Otp send sucessfully.", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()


@api.route("/changePassword")
@api.response(200, "password has been changes")
class ChangePassword(Resource):
    @api.doc('Change password')
    @api.expect(ChangePassword)
    def patch(self):
        '''Change password'''
        try:
            db = get_db()
            cur = db.cursor()
            if 'user_id' in session:
                formData = api.payload

                password = formData['currentPassword']
                newPassword = formData['newPassword']
                confirmPassword = formData['confirmPassword']
                if(newPassword != confirmPassword):
                    return({"status": False, "information": "current and new password are not same.", "error_code": "400", "error_message": "current and new password are not same."}, 400)

                sql = "UPDATE users SET password=(%s) WHERE id =(%s)"
                data = (str(generate_password_hash(password)),
                        str(session['user_id']))
                cur.execute(sql, data)
                db.commit()
                return({"status": True, "information": "User password sucessfully changed.", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return ('unauthorized')

        return view(**kwargs)

    return
