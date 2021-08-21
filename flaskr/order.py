from logging import log
from flaskr import client
from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
api = Namespace('order', description='Apis for  user')


orderDetails = api.model('updateUserDetails', {
    'status': fields.String(required=True),
    'orderDetails': fields.String(required=True),
    'productId': fields.String(required=True),
    'amount': fields.Integer(required=True),
})


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@api.route('')
@api.response(200, 'get logged in user details')
class createOrder(Resource):
    @ api.doc('Enter your  order details')
    @ api.expect(orderDetails)
    def post(self):
        try:
            db = get_db()
            cur = db.cursor()
            userId = session.get('user_id')
            if(userId):

                formData = api.payload
                status = formData["status"]
                orderDetails = formData['orderDetails']
                productId = formData['productId']
                amount = formData['amount']

                cur.execute(
                    "SELECT * from users WHERE id=(%s)", (str(userId),))
                user = cur.fetchone()
                sql = "insert into printpanindia.order(userId,clientId,status,productId,amount,orderDetails) values(%s,%s,%s,%s,%s,%s)"
                cur.execute(sql, (user["id"], user["clientId"],
                            status, productId, amount, orderDetails))
                db.commit()

                return({"status": True, "information": "Your order has been saved", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 400)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()

    def get(self):
        try:
            db = get_db()
            cur = db.cursor()
            userId = session.get('user_id')
            if(userId):

                sql = "select * from printpanindia.order where userId=(%s)"
                cur.execute(sql, (userId,))
                order = list(cur.fetchall())
                for elt in order:
                    elt["placedTime"] = str(elt['placedTime'])

                return({"orders": order, "status": True, "information": "", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 400)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()


@ api.route('/<int:id>')
@ api.doc(params={'id': 'update template by id'})
@ api.response(200, 'update orders')
class updateOrder(Resource):
    @ api.expect(orderDetails)
    def patch(self, id):
        try:
            db = get_db()
            cur = db.cursor()
            userId = session.get('user_id')
            if(userId):

                formData = api.payload
                status = formData["status"]
                orderDetails = formData['orderDetails']
                productId = formData['productId']
                amount = formData['amount']

                cur.execute(
                    "SELECT * from users WHERE id=(%s)", (str(userId),))
                user = cur.fetchone()

                sql = "update printpanindia.order set clinetId=(%s),userId=(%s),status=(%s),productId=(%s),amount=(%s),orderDetails=(%s) where id=(%s)"
                cur.execute(sql, (user["id"], user["clientId"],
                            status, productId, amount, orderDetails, id))
                db.commit()

                return({"status": True, "information": "Your order has been updated", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 400)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()

    def delete(self, id):
        try:
            db = get_db()
            cur = db.cursor()
            userId = session.get('user_id')
            if(userId):

                sql = "DELETE FROM printpanindia.order WHERE id=(%s)"
                cur.execute(sql, (id,))

                db.commit()

                return({"status": True, "information": "Your order has been deleted", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 400)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()
