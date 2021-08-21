from logging import log
from flaskr import client
from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
api = Namespace('product', description='Apis for  products')


productDetails = api.model('productDetails', {
    'imageUrl': fields.String(required=True),
    'productDescription': fields.Nested(api.model('productDescription', {
        'productCode': fields.Integer(required=True),
        'productName': fields.String(required=True),
        'size': fields.String(required=True),
        'quality': fields.String(required=True),
        'printQuality': fields.String(required=True),
        'productOptions': fields.String(required=True),
    })),
    'active': fields.Boolean(required=True),
})


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


@api.route('')
@api.response(200, 'get logged in user details')
class createProduct(Resource):
    @ api.doc('Enter your  order details')
    @ api.expect(productDetails)
    def post(self):
        try:
            db = get_db()
            cur = db.cursor()
            userId = session.get('user_id')
            if(userId):

                formData = api.payload
                imageUrl = formData["imageUrl"]
                productDescription = formData['productDescription']
                active = formData['active']

                sql = "insert into printpanindia.products(userId,imageUrl,productDescription,active) values(%s,%s,%s,%s)"
                cur.execute(
                    sql, (userId, imageUrl, productDescription, active))
                db.commit()

                return({"status": True, "information": "Your product has been saved", "error_code": "", "error_message": ""}, 201)
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

                sql = "select * from printpanindia.products where userId=(%s)"
                cur.execute(sql, (userId,))
                products = list(cur.fetchall())
                for elt in products:
                    elt["placedTime"] = str(elt['placedTime'])

                return({"products": products, "status": True, "information": "", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 400)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()


@ api.route('/<int:id>')
@ api.doc(params={'id': 'update products by id'})
@ api.response(200, 'update products')
class updateOrder(Resource):
    @ api.expect(productDetails)
    def patch(self, id):
        try:
            db = get_db()
            cur = db.cursor()
            userId = session.get('user_id')
            if(userId):

                formData = api.payload
                imageUrl = formData["imageUrl"]
                productDescription = formData['productDescription']
                active = formData['active']

                sql = "update products set imageUrl=(%s),productDescription=(%s),active=(%s) where id=(%s)"
                cur.execute(sql, (imageUrl, productDescription, active, id))
                db.commit()

                return({"status": True, "information": "Your product has been updated", "error_code": "", "error_message": ""}, 201)
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

                sql = "DELETE FROM printpanindia.product WHERE id=(%s)"
                cur.execute(sql, (id,))

                db.commit()

                return({"status": True, "information": "Your order has been deleted", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 400)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()
