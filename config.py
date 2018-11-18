import os
from app import app


'''
config class
'''

class Config(object):
    DEBUG=True
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ.get('trulysEmail')
    app.config['MAIL_PASSWORD'] = os.environ.get('trulysPassword')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = True
    DATABASE_URL = 'postgresql://postgres:crycetruly@localhost:5432/parcel_db'
    """Parent configuration class."""
    DEBUG = False
    SECRET = os.getenv('SECRET')


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True


class TestingConfig(Config):
    """Configurations for Testing."""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'postgresql://postgres:crycetruly@localhost:5432/parcel_db'


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

   