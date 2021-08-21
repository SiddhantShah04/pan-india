# import pyrebase


# firebase = pyrebase.initialize_app(config)
# storage = firebase.storage()
# path_on_cloud = "images/foo.jpg"

# path_local = "static/pil_text.png"
# #storage.child(path_on_cloud).put(path_local)
# #url = storage.child(path_on_cloud).put(path_local)
# #print("gs://"+url['bucket']+url['name'])
# # print(storage.child(path_on_cloud).put(path_local))

# print(storage.child("images/foo.jpg").get_url(config))


# import pyrebase
# import os

# config = {
#     "apiKey": "AIzaSyD516HWCuyZxTqWNiMWRE2JkGTKE9LRhzQ",
#     "authDomain": "printpanindia.firebaseapp.com",
#     "projectId": "printpanindia",
#     "storageBucket": "printpanindia.appspot.com",
#     "messagingSenderId": "921436240715",
#     "appId": "1:921436240715:web:771f502700c4736b8686ce",
#     "measurementId": "G-VMSGJZ86QG",
#     "databaseURL":"gs://printpanindia.appspot.com/"
# }
# firebase = pyrebase.initialize_app(config)
# storage = firebase.storage()
# my_image = "static/pil_text.png"

# # Upload Image
# storage.child(my_image).put(my_image)

# # Download Image
# # storage.child(my_image).download(filename="myself.jpg", path=os.path.basename(my_image))

# # Get url of image
# # auth = firebase.auth()
# email = "youremail@gmail.com"
# password = "yourpassword"
# # user = auth.sign_in_with_email_and_password(email, password)
# url = storage.child(my_image).get_url(config)
# print(url)


from firebase_admin import storage
from firebase_admin import credentials
import firebase_admin
import datetime


# Fetch the service account key JSON file contents
cred = credentials.Certificate("firebaseConfig.json")

# Initialize the app with a service account, granting admin privileges
app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'printpanindia.appspot.com',
}, name='storage')

path_local = "static/pil_text.png"
path_on_cloud = "1/images/foo.jpg"

bucket = storage.bucket(app=app)

# upload file
blob = bucket.blob(path_on_cloud)
outfile = path_local
blob.upload_from_filename(outfile)

# get link
# bucket.put(path_local)
blob = bucket.blob(path_on_cloud)

print(blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET'))
