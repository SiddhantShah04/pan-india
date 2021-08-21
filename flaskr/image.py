from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog
from werkzeug.security import check_password_hash, generate_password_hash
import re
from PIL import Image, ImageDraw, ImageFont
from flask import url_for, request, g
import json
from werkzeug.datastructures import FileStorage
import os
import glob
from flaskr.util.saveToFirebase import getUrl
from urllib.request import urlopen
import uuid

api = Namespace('images', description='Apis for Pan Print India')


createImage = api.model('CreateImage', {
    'name': fields.String(required=True, description="Name"),
    'designation': fields.String(required=True, description="Designation"),
    'department': fields.String(required=True, description="Department"),
    'imageWidth': fields.Integer(required=True, description="width"),
    'imageHeight': fields.Integer(required=True, description="Height")

})

createImage = api.model('Create Image', {
    'widthOfTemplate': fields.Integer(required=True, description="Width of template", example=570),
    'heightOfTemplate': fields.Integer(required=True, description="Height of template", example=570),
    'side': fields.String(required=True, example="front"),
    'imageUrl': fields.String(required=True, example=""),
    'dynamic_fields': fields.List(fields.Nested(
        api.model('dynamic_fields', {
            'fieldName': fields.String(required=True, example="Name"),
            'fieldType': fields.String(required=True, example="text or image"),
            'position': fields.Nested(api.model('position', {"x": fields.String(required=True, example="370"), "y": fields.String(required=True, example="377")})),
            'value': fields.String(required=True, example="text or image url"),
            'fontColor': fields.String(example="red"),
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
            user_id = session.get('user_id')
            if(user_id):
                db = get_db()
                cur = db.cursor()

                formData = api.payload
                widthOfTemplate = int(formData["widthOfTemplate"])
                heightOfTemplate = int(formData["heightOfTemplate"])
                imageUrl = formData['imageUrl']
                fileName = str(uuid.uuid4())
                side = formData['side']
                im = Image.open(urlopen(imageUrl))

                genrateImage = im.resize(
                    (widthOfTemplate, heightOfTemplate), Image.ANTIALIAS)
                imageWriter = ImageDraw.Draw(genrateImage)
                for elt in formData['dynamic_fields']:
                    positionX = int(elt['position']['x'])
                    positionY = int(elt['position']['y'])

                    if(elt['fieldType'] == 'text'):
                        fontName = elt['fontStyle']  # known section

                        font = ImageFont.truetype(
                            f"fonts/{fontName}", 15)
                        imageWriter.text(
                            (positionX, positionY), elt['value'], fill=elt['fontColor'], font=font)
                    elif(elt['fieldType'] == 'image'):
                        # add the image to specific position
                        imageUrl = elt["value"]
                        imageUrl = Image.open(urlopen(imageUrl))
                        offset = (positionX, positionX)

                        genrateImage.paste(imageUrl, offset)
                fileName = fileName+'.png'
                genrateImage.save(f'flaskr/static/{fileName}')
                image = getUrl(
                    user_id, f'flaskr/static/{fileName}', fileName)
                os.remove(f'flaskr/static/{fileName}')
                # image = request.host_url + \
                #     url_for('static', filename=fileName)

                sql = "INSERT INTO image(userId,imageUrl,side,fileName,dynamicFields) VALUES (%s,%s,%s,%s,%s)"
                data = (user_id, image, side, fileName,
                        str(formData['dynamic_fields']))

                cur.execute(sql, data)

                db.commit()
                return({'imageUrl': image, "status": True, "information": "image has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()

    def get(self):
        """get all templates of logged in client"""
        try:
            user_id = session.get('user_id')
            if(user_id):
                db = get_db()
                cur = db.cursor()

                sql = "SELECT * FROM image WHERE userId=%s"
                data = (user_id,)
                cur.execute(sql, data)
                orders = list(cur.fetchall())
                for elt in orders:
                    elt["placedTime"] = str(elt['placedTime'])

                return({'Data': orders, "status": True, "information": "image Url has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()


@api.route('/<int:id>')
@api.doc(params={'id': 'get template by id'})
class editImage(Resource):
    """get templates of logged in client by template id"""

    def get(self, id):
        try:
            db = get_db()

            cur = db.cursor()

            formData = api.payload
            user_id = session.get('user_id')
            if(user_id):

                sql = "SELECT * FROM image WHERE userId=%s and id = %s"

                data = (user_id, id)
                cur.execute(sql, data)
                imageData = cur.fetchone()

                imageData["updatedAt"] = str(imageData['updatedAt'])
                imageData["createdAt"] = str(imageData['createdAt'])
                return({'data': imageData, 'status': True, "information": 'Client template data', "error_code": "", "error_message": ""}, 200)
            else:
                return({"status": False, "information": 'Unauthorized access', "error_code": "500", "error_message": "User have to logged in first."}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

        finally:
            cur.close()

    @ api.expect(createImage)
    def patch(self, id):
        try:
            user_id = session.get('user_id')
            if(user_id):
                db = get_db()
                cur = db.cursor()

                formData = api.payload
                widthOfTemplate = int(formData["widthOfTemplate"])
                heightOfTemplate = int(formData["heightOfTemplate"])
                imageUrl = formData['imageUrl']
                side = formData['side']
                sql = "SELECT fileName FROM image WHERE userId=%s and id=%s"
                data = (user_id, id)
                cur.execute(sql, data)
                fileName = cur.fetchone()['fileName']
                im = Image.open(urlopen(imageUrl))

                genrateImage = im.resize(
                    (widthOfTemplate, heightOfTemplate), Image.ANTIALIAS)
                imageWriter = ImageDraw.Draw(genrateImage)
                for elt in formData['dynamic_fields']:
                    positionX = int(elt['position']['x'])
                    positionY = int(elt['position']['y'])

                    if(elt['fieldType'] == 'text'):

                        # fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 20)
                        imageWriter.text(
                            (positionX, positionY), elt['value'], fill=elt['fontColor'])
                    elif(elt['fieldType'] == 'image'):
                        # add the image to specific position
                        imageUrl = elt["value"]
                        imageUrl = Image.open(urlopen(imageUrl))
                        offset = (positionX, positionX)

                        genrateImage.paste(imageUrl, offset)

                genrateImage.save(f'flaskr/static/{fileName}')
                image = getUrl(
                    user_id, f'flaskr/static/{fileName}', fileName)

                sql = "UPDATE image SET userId=%s,imageUrl=%s,side=%s,fileName=%s,dynamicFields=%s where clientId=%s and id=%s"
                data = (user_id, image, side, fileName,
                        str(formData['dynamic_fields']), user_id, id)
                cur.execute(sql, data)
                os.remove(f'flaskr/static/{fileName}')
                db.commit()
                return({'imageUrl': image, "status": True, "information": "image has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            cur.close()


@api.route('/createImageUrl')
class CreateImageUrl(Resource):
    @api.doc('Create Image url')
    @api.expect(upload_parser)
    def post(self):
        try:
            user_id = session.get('user_id')
            if(user_id):
                args = upload_parser.parse_args()
                file = args.get('file')
                file.save(os.path.join('flaskr/static', file.filename))

                # perform transforms

                fileData = getUrl(
                    user_id, f'flaskr/static/{file.filename}', file.filename)
                os.remove(f'flaskr/static/{file.filename}')
                # file.save(os.path.join('flaskr/static', file.filename))
                # fileData = {'fileUrl': request.host_url +
                #             url_for('static', filename=file.filename), 'fileName': file.filename}

                return({'imageUrl': fileData, "status": True, "information": "image Url has been created", "error_code": "", "error_message": ""}, 201)
            else:
                return({"status": False, "information": "unauthorized", "error_code": "", "error_message": ""}, 500)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)


@api.route('/getFonts')
class GetFonts(Resource):
    @api.doc('get fonts')
    def get(self):

        filename = "ttf"  # known section
        direc = "fonts/"

        matches = [fname for fname in os.listdir(
            direc) if fname.endswith(filename)]

        return(matches)
