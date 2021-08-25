from flask_restx import Namespace, Resource, fields, reqparse
from flask import session
from flaskr.db import get_db
import json
import uuid

import ast
from . import activityLog
from flaskr import create_app
from flask_mail import Mail, Message
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
    'billingAndPaymentTerms': fields.Nested(
        api.model('billingAndPaymentTerms', {
            'billing': fields.String(required=True),
            'billingReq': fields.String(required=True),
            'billingCycle': fields.Integer(required=True),
            'creditLimit': fields.Integer(required=True),
            'gstNo': fields.Integer(required=True),
            'billingAddressBranch': fields.Integer(required=True),
        })
    ),
    'applicationSettingData': fields.Nested(
        api.model('applicationSettingData', {
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
    'vendor': fields.Nested(api.model('vendor', {
        'email': fields.String(required=True, example="siddhantshah04@gmail.com"),
        'phone': fields.String(required=True, example="8828286463"),

    }))
})

updateClientDetails = api.model('updateClientDetails', {
    'clientId': fields.String(required=True),
    'itemsToUpdate': fields.List(fields.Nested(api.model('item', {'column Name': fields.String}))),

})
# f5ff1719-7dc5-4be8-bcd0-f071b449
tempArray = ['companyDetails', 'procurements', 'admin', 'accounts', 'specification', 'packingCourierDetails', 'packingTeam',
             'packingCourierDetails', 'billingAndPaymentTerms', 'applicationSettingData', 'information', "vendor"]

statusUpdate = api.model('statusUpdate', {
    'status': fields.Integer(required=True, description=' 0 - Proper data, 1 - Active Client, 2 - Wrong Data , 3 - Suspended Client'),
})


# newclientRegistation
@api.route('/')
class ClientDetails(Resource):

    # @api.marshal_with(clientDetails, code=201, description='Client data added')
    def get(self):
        try:
            db = get_db()
            cur = db.cursor()
            if 'user_id' in session:

                # json.dumps(users )
                sql = "SELECT * FROM users WHERE id=%s"
                data = (str(session['user_id']),)
                cur.execute(sql, data)
                userData = cur.fetchone()
                sql = "SELECT * FROM clientDetails WHERE clientId=%s"
                data = (str(userData['clientId']),)
                cur.execute(sql, data)
                clientData = cur.fetchone()
                print(clientData)
                # Array contains data in dict
                tempData = ['companyDetails', 'procurements', 'admin', 'accounts', 'specification', 'packingCourierDetails', 'packingTeam',
                            'billingAndPaymentTerms', 'settings']
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
            data = {}
            error = False
            for elt in tempArray:
                if(elt in formData.keys()):
                    data[elt] = formData[elt]
                else:
                    data[elt] = None
                    error = False
            data2 = {}
            data2["clientId"] = str(uuid.uuid4())
            data2["companyName"] = formData["companyDetails"]["companyName"] if formData["companyDetails"]["companyName"] else None
            data2["createdBy"] = ""
            data2["information"] = "information"
            data2["status"] = 2
            # if(error):
            #     data["status"] = False
            #     data2["status"] = 2
            #     data["error"] = f"{[key for (key,value) in data.items() if value == None ]} Not found"

            # else:
            #     data2["status"] = 0
            #     data["status"] = True

            sql = "INSERT INTO clientConfiguration(clientId,companyName,createdBy,information,status) VALUES (%s,%s,%s,%s,%s)"
            cur.execute(sql, tuple(data2.values()))
            data["vendor"] = {}
            # data["packingCourier"] = {}
            data["status"] = 1
            data["information"] = {}
            # print(data)
            data["clientId"] = data2["clientId"]

            #!packingCourier settings
            sql = "INSERT INTO clientDetails(companyDetails,procurements,admin,accounts,specification,packingCourierDetails,packingTeam,billingAndPaymentTerms,applicationSettingData,information,vendor,status,clientId) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, tuple(data.values()))
            db.commit()

            if(error):
                return({'status': data["status"], 'error_code': 400, 'error_message': f"{[key for (key,value) in data.items() if value == None ]} Not found"}, 400)

            return({"status": True, "information": "The data has been recorded soon a support person will contact you", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()


@api.route("/<int:id>")
@api.doc(params={'id': 'Enter Client ID'})
class EditClient(Resource):
    @api.expect(clientDetails)
    def patch(self, id):
        try:
            db = get_db()
            cur = db.cursor()
            formData = api.payload
            user_id = session.get('user_id')
            data = {}
            error = False

            if(user_id):

                for elt in tempArray:
                    if(elt in formData.keys()):
                        data[elt] = formData[elt]

                    else:
                        data[elt] = None
                        error = True

                companyName = formData["companyDetails"]["companyName"] if formData["companyDetails"]["companyName"] else None
                print(companyName)
                sql = "Update  clientConfiguration  set companyName=%s,createdBy=%s,information=%s where id=%s"
                cur.execute(sql, (
                    companyName, "", formData["information"], id))

                if(error):
                    data["status"] = False
                    data["error"] = f"{[key for (key,value) in data.items() if value == None ]} Not found"
                else:
                    data["status"] = True
                db.commit()

                return({"status": True, "information": "The Client details has been updated.", "error_code": "", "error_message": ""}, 201)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()


@api.route("/statusUpdate/<string:id>")
@api.doc(params={'id': 'Enter Client ID'})
class StatusUpdate(Resource):
    @api.expect(statusUpdate)
    def patch(self, id):
        try:
            db = get_db()
            cur = db.cursor()
            formData = api.payload
            sql = "select * from users where clientId=%s"
            data = (id,)
            cur.execute(sql, data)
            userData = cur.fetchone()

            sql = "Update  clientConfiguration  set status=%s where clientId=%s"
            cur.execute(sql, (formData["status"], id))

            db.commit()
            # sendStatusChangeMail(create_app())

            message = f"""
    
            <h1>Hello, </h1>
            <br/>
                Your status has been changed. 
                
            """

            mail = Mail(create_app())
            sender = "siddhantshah044@gmail.com"
            receiver = userData["email"]
            msg = Message(subject="message", sender=sender,
                          recipients=[receiver])
            msg.html = message

            mail.send(msg)

            return({"status": True, "information": "The Client status has been updated.", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            pass
            cur.close()
