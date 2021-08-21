from logging import log
from flaskr import client
from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog
from werkzeug.security import check_password_hash, generate_password_hash
import re
import json
import datetime
api = Namespace('user', description='Apis for  user')


updateUserDetails = api.model('updateUserDetails', {
    'clientId': fields.String(required=True),
    'itemsToUpdate': fields.List(fields.Nested(api.model('item', {'column Name': fields.String}))),

})


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@api.route('')
@api.response(200, 'get logged in user details')
class EditUser(Resource):
    @api.doc('editUser')
    @api.expect(updateUserDetails)
    def patch(self):
        try:
            db = get_db()
            cur = db.cursor()
            if 'user_id' in session:

                formData = api.payload

                for elt in formData['itemsToUpdate']:
                    for key, value in elt.items():

                        data = f"{key} = (%s)"
                        sql2 = "update users set " + \
                            data+" where clientId = (%s)"
                        cur.execute(
                            sql2, (value, str(formData['clientId'])))
                db.commit()

                return({"status": True, "information": "The user data has been updated", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": 'Unauthorized access', "error_code": "500", "error_message": "User have to logged in first."}, 500)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()

    @api.doc('Get users details')
    def get(self):

        try:
            db = get_db()
            cur = db.cursor()
            if 'user_id' in session:

                sql = "SELECT * FROM users WHERE userId=%s"
                data = (str(session['user_id']),)
                cur.execute(sql, data)

                userData = cur.fetchone()
                del userData["password"]

                return({'data': json.dumps(userData, default=myconverter), 'status': True, "information": 'Client details', "error_code": "", "error_message": ""}, 200)
            else:
                return({"status": False, "information": 'Unauthorized access', "error_code": "500", "error_message": "User have to logged in first."}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()
