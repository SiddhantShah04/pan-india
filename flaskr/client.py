from flask_restx import Namespace, Resource, fields, reqparse
from flask import session
from flaskr.db import get_db
import json
import uuid
import re
import ast
from . import activityLog
api = Namespace('newClientRegistration', description='Client data')

#   'companyDetails': fields.List(fields.Nested(api.model('TheModel', {'a': fields.String}))),
data = api.model('Runtime', {
    'name': fields.String(required=True),
    'designation': fields.String(required=True),
    'tel': fields.Integer(required=True),
    'mobile': fields.Integer(required=True, example=1236547890),
    'headOfficeEmail': fields.String(required=True, example="siddhantshah04@gmail.com"),
    'email': fields.String(required=True, example="siddhantshah04@gmail.com"),
    'approvalAuth': fields.Integer(required=True),
})

clientDetails = api.model('Client Data', {
    'companyDetails': fields.Nested(
        api.model('companyDetails', {
            'companyName': fields.String(required=True),
            'companyAddress': fields.String(required=True),
            'companyTel': fields.String(required=True),
            'companyEmail': fields.String(required=True, example="siddhantshah04@gmail.com"),
            'headOfficeAddress': fields.String(required=True),
            'headOfficeEmail': fields.String(required=True, example="siddhantshah04@gmail.com"),
            'companyGst': fields.String(required=True),
            'apiLink': fields.Url(required=True),
            'whiteList': fields.String(required=True),
            'itRequirement': fields.String(required=True)
        })
    ),
    'procurements': fields.Nested(data),
    'admin': fields.Nested(data),
    'accounts': fields.Nested(data),

    'specification': fields.Nested(
        api.model('specification', {
            'name': fields.String(required=True),
            'quality': fields.String(required=True),
            'size': fields.String(required=True),
            'printing': fields.String(required=True),
            'mode': fields.String(required=True),
            'side': fields.String(required=True),
            'minQty': fields.Integer(required=True),
            'rateApproved': fields.Integer(required=True),
            'specimen': fields.String(required=True),
            'code': fields.Integer(required=True),
            'productGst': fields.Integer(required=True),
            'productShipment': fields.Integer(required=True),

        })
    ),
    'packingCourierDetails': fields.Nested(
        api.model('packingCourierDetails', {
            'courierName': fields.String(required=True),
            'accountNo': fields.Integer(required=True),
            'address': fields.String(required=True),
            'contactPerson': fields.String(required=True, example="siddhant shah"),
            'tel': fields.Integer(required=True),
            'mob': fields.Integer(required=True, example=8828286463),
            'email': fields.String(required=True),
            'apiLink': fields.Url(required=True),
            'link': fields.String(required=True),
            'link': fields.String(required=True)
        })
    ),
    'packingTeam': fields.Nested(
        api.model('packingTeam', {
            'name': fields.String(required=True),
            'designation': fields.String(required=True),
            'tel': fields.Integer(required=True),
            'mobile': fields.Integer(required=True, example=8828286463),
            'email': fields.String(required=True),

        })
    ),
    'packingCourier': fields.String(required=True, description=''),
    'billing': fields.Nested(
        api.model('billing', {
            'billing': fields.String(required=True),
            'billingReq': fields.String(required=True),
            'billingCycle': fields.Integer(required=True),
            'creditLimit': fields.Integer(required=True),
            'gstNo': fields.Integer(required=True),
            'billingAddressBranch': fields.Integer(required=True),
        })
    ),
    'settings': fields.Nested(
        api.model('setting', {
            'autoInvoice': fields.String(required=True),
            'payOnAccount': fields.String(required=True),
            'salesAgentName': fields.String(required=True),
            'creditLimit': fields.Boolean(required=True),
            'department': fields.Boolean(required=True),
            'quickCheckout': fields.Boolean(required=True),
            'showPriceToCustomer': fields.Boolean(required=True),
            'orderApproval': fields.Boolean(required=True),
            'fixBillingAddr': fields.Boolean(required=True),
            'enableAuth': fields.Boolean(required=True),
            'paymentOptions': fields.String(required=True),
            'shippingOptions': fields.String(required=True),
            'corporateProfile': fields.String(required=True),
            'cms': fields.String(required=True),
            'link': fields.String(required=True),
            'sideBar': fields.String(required=True),
            'banner': fields.String(required=True),
            'languageOptions': fields.String(required=True),
        })
    ),
    'information': fields.String(required=True, description=''),

    'errorMessage': fields.String(required=True, description=''),
})

updateClientDetails = api.model('updateClientDetails', {
    'clientId': fields.String(required=True),
    'itemsToUpdate': fields.List(fields.Nested(api.model('item', {'column Name': fields.String}))),

})


def checkEmail(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if(True):
        return(False)
    else:
        return(True)


# newclientRegistation
@api.route('/')
class ClientDetails(Resource):

    # @api.marshal_with(clientDetails, code=201, description='Client data added')
    def get(self):

        try:
            db = get_db()

            cur = db.cursor()

            formData = api.payload
            if 'user_id' in session:

                sql = "select clientId from users where id = %s"
                data = (session['user_id'],)

                cur.execute(sql, data)
                # json.dumps(users)
                user = cur.fetchone()

                sql = "SELECT * FROM clientDetails WHERE clientId=%s"

                data = (str(user['clientId']),)
                cur.execute(sql, data)
                clientData = cur.fetchone()

                # Array contains data in dict
                tempData = ['companyDetails', 'procurements', 'admin', 'accounts', 'specification', 'packingCourierDetails', 'packingTeam',
                            'billing', 'settings', ]
                for key in clientData.keys():
                    if(key in tempData):
                        clientData[key] = ast.literal_eval(clientData[key])
                    else:
                        clientData[key] = str(clientData[key])

                return({'data': clientData, 'status': True, "information": 'Client details', "error_code": "", "error_message": ""}, 200)

            else:
                return({"status": False, "information": 'Unauthorized access', "error_code": "500", "error_message": "User have to logged in first."}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()

    @ api.doc('Enter Client details')
    @ api.expect(clientDetails)
    def post(self):
        '''Client details data submit'''
        try:
            db = get_db()
            cur = db.cursor()
            formData = api.payload

            tempArray = ['companyDetails', 'procurements', 'admin', 'accounts', 'specification', 'packingCourierDetails', 'packingTeam',
                         'packingCourier', 'billing', 'settings', 'information']
            data = {}
            additionalErrorMessage = []
            invalidEmail = False
            error = False
            for elt in tempArray:
                if(elt in formData.keys()):
                    data[elt] = formData[elt]

                    # if( type(formData[elt]) is dict and ("email" in formData[elt].keys() or "headOfficeEmail" in formData[elt].keys() or "companyEmail" in formData[elt].keys() ) ):

                    #     if("email" in formData[elt].keys()):
                    #         invalidEmail =  True
                    #         additionalErrorMessage.append("Email")
                    #         data[elt]["email"] = str(checkEmail(formData[elt].values()) if checkEmail(formData[elt].values()) else None)
                    #     if("headOfficeEmail" in formData[elt].keys()):
                    #         invalidEmail =  True
                    #         additionalErrorMessage.append("Head Office Email")
                    #         data[elt]["headOfficeEmail"] = checkEmail(formData[elt].values()) if checkEmail(formData[elt].values()) else None
                    #     if("companyEmail" in formData[elt].keys()):
                    #         invalidEmail =  True
                    #         additionalErrorMessage.append("Company Email")
                    #         data[elt]["companyEmail"] = checkEmail(formData[elt].values()) if checkEmail(formData[elt].values()) else None

                else:
                    data[elt] = None
                    error = True

            data2 = {}
            data2["clientId"] = str(uuid.uuid4())
            data2["companyName"] = formData["companyDetails"]["companyName"] if formData["companyDetails"]["companyName"] else None
            data2["createdBy"] = ""
            data2["information"] = data["information"]

            if(error):
                data["status"] = False
                data["error"] = f"{[key for (key,value) in data.items() if value == None ]} Not found"

            else:
                data["status"] = True

            sql = "INSERT INTO clientConfiguration(clientId,companyName,createdBy,information) VALUES (%s,%s,%s,%s)"
            cur.execute(sql, tuple(data2.values()))
            data["clientId"] = data2["clientId"]

            sql = "INSERT INTO clientDetails(companyDetails,procurements,admin,accounts,specification,packingCourierDetails,packingTeam,packingCourier,billing,settings,information,status,clientId) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            cur.execute(sql, tuple(data.values()))

            db.commit()
            # if(invalidEmail):
            #     return({'status':False,'error_code':400,'error_message' :   f"{[x for x in additionalErrorMessage]} is invalid" },400 )
            if(error):
                return({'status': data["status"], 'error_code': 400, 'error_message': f"{[key for (key,value) in data.items() if value == None ]} Not found"}, 400)

            activityLog.activity(0, "Client", f" With client Id " +
                                 data2["clientId"] + "registered", "clientConfiguration and clientDetails")

            return({"status": True, "information": "The Client has been registered", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()

    # @api.route('/id')
    # @api.doc(params={'id': 'An ID'})
    # def get(id):
    #     print(id)

    @ api.expect(updateClientDetails)
    def patch(self):

        try:
            db = get_db()
            cur = db.cursor()
            formData = api.payload
            print(formData['clientId'])
            for elt in formData['itemsToUpdate']:
                for key, value in elt.items():

                    data = f"{key} = (%s)"
                    sql2 = "update clientDetails set " + \
                        data+" where clientId = (%s)"
                    cur.execute(
                        sql2, (value, str(formData['clientId'])))
                    if(key == "companyDetails"):
                        newValue = ast.literal_eval(value)
                        sql2 = "update clientConfiguration set companyName=(%s) where clientId = (%s)"
                        cur.execute(
                            sql2, (newValue["companyName"], formData['clientId']))
            db.commit()

            # user_id = session['user_id']
            # tempData = ["status", "isActive"]
            # print(formData)

            # status = "status"
            # formValue = tuple(f"{status} = (%s)")

            # sql = "update clientDetails set status = (%s) where ID = (%s)"
            # sql2 = "update clientDetails set "+ formValue+" where ID = (%s)"

            # print(sql,sql2)
            # cur.execute(sql2,("1",4))
            # # db.commit()

            return({"status": True, "information": "The Client data has been updated", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()

        # @app.route('/search/<param1>/<param2>/<param3>')
            # def get(param1, param2, param3):
            #     cur = mysql.connect().cursor()
            #     cur.execute('''select * from maindb.maintable where field1 = %s and field2 = %s and field3 = %s''',
            #                 (param1, param2, param3))
            #     r = [dict((cur.description[i][0], value)
            #          for i, value in enumerate(row)) for row in cur.fetchall()]
            #     return jsonify({'results': r})python3 -m flask run


# @api.route('/<int:id>')
# class GetClientData(Resource):
#     @api.doc(params={'id': 'An ID'})
