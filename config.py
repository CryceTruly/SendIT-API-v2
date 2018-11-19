import os
from app import app


'''
config class
'''

class Config(object):
    """Parent configuration class."""
    DEBUG=True
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get('trulysEmail')
    app.config['MAIL_PASSWORD'] = os.environ.get('trulysPassword')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = True
    DATABASE_URL = 'postgresql://postgres:crycetruly@localhost:5432/sendit'
    SECRET = os.environ.get('trulysSecret')

class DevelopmentConfig(Config):
    """Configurations for Testing."""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'postgresql://postgres:crycetruly@localhost:5432/sendit'


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False
    DATABASE_URL = 'postgresql://zbfspwkaubgzur:34f1f0514ad1e4685cd76e0b7ba5150d1d8c9d96fd1eb233bc7f5f792b546ba9@ec2-54-225-110-156.compute-1.amazonaws.com:5432/'
app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

   