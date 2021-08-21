from waitress import serve
from flaskr.__init__ import create_app

serve(create_app(),host="0.0.0.0",port=5000)