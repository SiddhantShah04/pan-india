from flask_restx import Namespace, Resource, fields, abort
from flask import session
from flaskr.db import get_db
from . import activityLog
from werkzeug.security import check_password_hash, generate_password_hash
import re
from PIL import Image, ImageDraw, ImageFont
from flask import url_for, request
import json
from werkzeug.datastructures import FileStorage
import os
api = Namespace('images', description='Apis for Pan Print India')


createImage = api.model('CreateImage', {
    'name': fields.String(required=True, description="Name"),
    'designation': fields.String(required=True, description="Designation"),
    'department': fields.String(required=True, description="Department"),
    'imageWidth': fields.Integer(required=True, description="width"),
    'imageHeight': fields.Integer(required=True, description="Height")

})

createImage = api.model('Create Image', {
    'imageBackgroundColor': fields.String(required=True, description="Image Background Color", example="white"),
    'widthOfTemplate': fields.Integer(required=True, description="Width of template", example=570),
    'heightOfTemplate': fields.Integer(required=True, description="Height of template", example=570),
    'dynamic_fields': fields.List(fields.Nested(

        api.model('dynamic_fields', {
            'fieldName': fields.String(required=True, example="Name"),
            'fieldType': fields.String(required=True, example="text"),
            'side': fields.String(required=True, example="front"),
            'position': fields.Nested(api.model('position', {"x": fields.String(required=True, example="370"), "y": fields.String(required=True, example="377")})),
            'value': fields.String(required=True, example="Siddhant Shah"),
            'fontColor': fields.String(required=True, example="red"),
            'fontStyle': fields.String(required=True, example="roboto"),
        })
    )), })


upload_parser = api.parser()
upload_parser.add_argument('file',
                           location='files',
                           type=FileStorage)
# createImageUrl = api.model('create Image Url', {
#     'image': fields.file(required=True, description="Image Background Color", example="white"),

# })


@ api.route('')
class CreateImage(Resource):
    @ api.doc('Enter your  image details')
    @ api.expect(createImage)
    def post(self):
        try:
            formData = api.payload
            widthOfTemplate = int(formData["widthOfTemplate"])
            heightOfTemplate = int(formData["heightOfTemplate"])
            img = Image.new('RGB', (widthOfTemplate, heightOfTemplate),
                            color=formData['imageBackgroundColor'])
            d = ImageDraw.Draw(img)
            for elt in formData['dynamic_fields']:
                positionX = int(elt['position']['x'])
                positionY = int(elt['position']['y'])
                # fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 20)

                d.text(
                    (positionX, positionY), elt['value'], fill=elt['fontColor'])

            # img.save(os.path.join('flaskr/static', "pil_text.png"))

            img.save('flaskr/static/pil_text.png')
            image = request.remote_addr + \
                url_for('static', filename='pil_text.png')

            return({'imageUrl': image, "status": True, "information": "image has been created", "error_code": "", "error_message": ""}, 201)

        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)
        finally:
            pass


@api.route('/createImageUrl')
class CreateImageUrl(Resource):
    @api.doc('Create Image url')
    @api.expect(upload_parser)
    def post(self):
        try:
            args = upload_parser.parse_args()
            file = args.get('file')
            # file.save(''+file.filename)
            file.save(os.path.join('flaskr/static', file.filename))
            fileUrl = request.remote_addr + \
                url_for('static', filename=file.filename)
            return({'imageUrl': fileUrl, "status": True, "information": "image Url has been created", "error_code": "", "error_message": ""}, 201)
        except Exception as e:
            return({"status": False, "information": str(e), "error_code": "500", "error_message": "internal server error"}, 500)

# https://flask-restx.readthedocs.io/en/latest/_modules/flask_restx/api.html
# https://stackoverflow.com/questions/55868026/pillow-how-can-i-paste-a-image-on-another-image
