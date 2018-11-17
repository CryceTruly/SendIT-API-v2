from app.views.parcels import ap
from app.views.users import user_print
from flask import Flask
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

app.register_blueprint(ap)
app.register_blueprint(user_print)
