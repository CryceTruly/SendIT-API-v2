import os
from app import app


'''
config class
'''
class Config():
    DEBUG=True
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get('trulysEmail')
    app.config['MAIL_PASSWORD'] = os.environ.get('trulysPassword')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = True
