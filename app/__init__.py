from app.views.parcels import ap
from app.views.users import auth
from app.views.search import search
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger


app=Flask(__name__)
Swagger(app)
app.register_blueprint(ap)
app.register_blueprint(auth)
app.register_blueprint(search)
