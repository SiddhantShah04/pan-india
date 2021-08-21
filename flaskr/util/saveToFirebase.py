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


def getUrl(user_id, file, name):

    path_local = file
    path_on_cloud = f"{user_id}/images/{name}"

    bucket = storage.bucket(app=app)

    # upload file
    blob = bucket.blob(path_on_cloud)
    outfile = path_local
    blob.upload_from_filename(outfile)

    # get link
    # bucket.put(path_local)
    blob = bucket.blob(path_on_cloud)

    return(blob.generate_signed_url(datetime.timedelta(seconds=300000), method='GET'))
