from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog

import re
from PIL import Image, ImageDraw, ImageFont
from flask import url_for, request, g
import json
from werkzeug.datastructures import FileStorage
import os
from io import StringIO

from flaskr.util.saveToFirebase import getUrl
from urllib.request import urlopen
import uuid
from flaskr.util.createImage import drawImage
api = Namespace('images', description='Apis for Pan Print India')

# createImage = api.model('CreateImage', {
#     'name': fields.String(required=True, description="Name"),
#     'designation': fields.String(required=True, description="Designation"),
#     'department': fields.String(required=True, description="Department"),
#     'imageWidth': fields.Integer(required=True, description="width"),
#     'imageHeight': fields.Integer(required=True, description="Height"),
#     'templateId': fields.Integer(required=True, description="id of template"),
# })

createImage = api.model('Create Image', {
    'widthOfTemplate': fields.Integer(required=True, description="Width of template", example=570),
    'heightOfTemplate': fields.Integer(required=True, description="Height of template", example=570),
    'side': fields.String(required=True, example="front"),
    'imageUrl': fields.String(example=""),
    'templateId': fields.Integer(required=True, description="id of template"),
    'dynamicFields': fields.List(fields.Nested(
        api.model('dynamicFields', {
            'fieldName': fields.String(example="Name"),
            'fieldType': fields.String(example="text or image"),
            'position': fields.Nested(api.model('position', {"x": fields.String(example="370"), "y": fields.String(example="377")})),
            'value': fields.String(example="text or image url"),
            'fontColor': fields.String(example="red"),
            'fontSize': fields.Integer(example=14),
            'fontStyle': fields.String(example="roboto"),
        })
    )), })

upload_parser = api.parser()
upload_parser.add_argument('file',
                           location='files',
                           type=FileStorage, required=True)

# createImageUrl = api.model('create Image Url', {
#     'image': PpVP5DndgSx6CVpUbPrs fields.String(required=True, description="Image Background Color", example="white"),

# })


@ api.route('')
class CreateImage(Resource):
    @ api.doc('Enter your  image details')
    @ api.expect(createImage)
    def post(self):
        try:
            # user_id = session.get('user_id')
            user_id = 2
            if(True):
                db = get_db()
                cur = db.cursor()

                formData = api.payload
                genrateImage = drawImage(formData)

                fileName = str(uuid.uuid4())
                side = formData['side']

                fileName = fileName+'.png'
                genrateImage.save(f'flaskr/static/{fileName}')
                imageUrl = getUrl(
                    user_id, f'flaskr/static/{fileName}', fileName, side)
                os.remove(f'flaskr/static/{fileName}')
                # image = request.host_url + \
                #     url_for('static', filename=fileName)

                sql = "INSERT INTO image(userId,imageUrl,templateId,side,fileName,widthOfTemplate,heightOfTemplate,dynamicFields) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
                data = (user_id, formData["imageUrl"], formData["templateId"], side, fileName, formData['widthOfTemplate'], formData['heightOfTemplate'],
                        json.dumps(formData['dynamicFields']))

                cur.execute(sql, data)
                db.commit()

                cur.execute("SELECT LAST_INSERT_ID()",)
                ImageData = cur.fetchone()
                print(ImageData["LAST_INSERT_ID()"], cur.lastrowid)
                return({'ImageData': json.dumps({'imageUrl': imageUrl, 'imageId': ImageData["LAST_INSERT_ID()"]}), "status": True, "information": "image has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()

    def get(self):
        """get all templates of logged in client"""
        try:
            # user_id = session.get('user_id')
            if(True):
                db = get_db()
                cur = db.cursor()

                # sql = "SELECT * FROM image WHERE userId=%s"
                sql = "SELECT * FROM image where id=100"

                # data = (user_id,)
                cur.execute(sql, )
                orders = cur.fetchall()

                # genrateImage = drawImage()

                for elt in orders:

                    elt["createdAt"] = str(elt['createdAt'])
                    elt["updatedAt"] = str(elt['updatedAt'])

                return({'data': orders, "status": True, "information": "image Url has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()


@ api.route('/<int:id>')
@ api.doc(params={'id': 'get template by id'})
class editImage(Resource):
    """get templates of logged in client by template id"""

    def get(self, id):
        """get all templates of logged in client"""
        try:
            # user_id = session.get('user_id')
            user_id = 2

            if(True):
                db = get_db()
                cur = db.cursor()
                print(id)
                # sql = "SELECT * FROM image WHERE userId=%s"
                sql = "SELECT * FROM image where userId=(%s) and templateId=(%s)"

                # data = (user_id,)
                cur.execute(sql, (user_id, id))
                orders = cur.fetchall()

                # genrateImage = drawImage()

                for elt in orders:

                    elt["createdAt"] = str(elt['createdAt'])
                    elt["updatedAt"] = str(elt['updatedAt'])

                return({'data': orders, "status": True, "information": "image Url has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()

    @ api.expect(createImage)
    def patch(self, id):
        try:
            # user_id = session.get('user_id')
            user_id = 2

            if(user_id):
                db = get_db()
                cur = db.cursor()

                formData = api.payload

                side = formData['side']
                # sql = "SELECT fileName FROM image WHERE userId=%s and id=%s"
                sql = "SELECT fileName,imageUrl FROM image WHERE userId=%s and id=%s"
                data = (user_id, id)
                cur.execute(sql, data)
                temp = cur.fetchone()
                fileName = temp['fileName']
                formData["imageUrl"] = temp["imageUrl"]

                genrateImage = drawImage(formData)
                genrateImage.save(f'flaskr/static/{side}/{fileName}')
                image = getUrl(
                    user_id, f'flaskr/static/{side}/{fileName}', fileName, side)

                sql = "UPDATE image SET userId=%s,side=%s,fileName=%s,dynamicFields=%s where userId=%s and id=%s"
                data = (user_id, side, fileName,
                        json.dumps(formData['dynamicFields']), user_id, id)
                cur.execute(sql, data)
                os.remove(f'flaskr/static/{side}/{fileName}')
                db.commit()
                return({'imageUrl': image, "status": True, "information": "image has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()


@ api.route('/createImageUrl/<string:side>')
@ api.doc(params={'side': 'side of template'})
class CreateImageUrl(Resource):
    @ api.doc('Create Image url')
    @ api.expect(upload_parser)
    def post(self, side):
        try:
            user_id = session.get('user_id')
            if(True):
                args = upload_parser.parse_args()
                file = args.get('file')
                file.save(os.path.join('flaskr/static', file.filename))

                # perform transforms

                fileData = getUrl(
                    user_id, f'flaskr/static/{file.filename}', file.filename, side)
                os.remove(f'flaskr/static/{file.filename}')
                # file.save(os.path.join('flaskr/static', file.filename))
                # fileData = {'fileUrl': request.host_url +
                #             url_for('static', filename=file.filename), 'fileName': file.filename}

                return({'imageUrl': fileData, "status": True, "information": "image Url has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)


@ api.route('/getFonts')
class GetFonts(Resource):
    @ api.doc('get fonts')
    def get(self):

        filename = "ttf"  # known section
        direc = "fonts/"

        matches = [fname for fname in os.listdir(
            direc) if fname.endswith(filename)]

        return(matches)
