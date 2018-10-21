import os
import sys
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
WIN = sys.platform.startswith('win')
if WIN:
    prefix='sqlite:///'
else:
    prefix='sqlite:////'

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY','soft lipapapa')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    # MAIL_USE_SSL = True
    MAIL_USERNAME = 'apikey'
    FLASKY_MAIL_SENDER = 'noreply@ywslab.com'
    MAIL_USE_TLS = True
    MAIL_PASSWORD = os.getenv('SENDGRID_API_KEY')
    NEWBLOG_POST_PER_PAGE = 10
    NEWBLOG_MANAGE_POST_PER_PAGE = 15
    NEWBLOG_COMMENT_PER_PAGE = 15
    WTF_CSRF_ENABLED = True
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_FILE_UPLOADER = 'editor.upload'
    CKEDITOR_HEIGHT = 400
    UPLOADED_PATH = os.path.join(basedir,'newblog/static/uploads')
    CKEDITOR_ENABLE_CODESNIPPET=True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    # DROPZONE_MAX_FILE_SIZE = 10
    # DROPZONE_MAX_FILES = 30
    # MAX_CONTENT_LENGTH = 10*1024*1024
    # DROPZONE_ALLOWED_FILE_TYPE = 'image'
    # DROPZONE_ENABLE_CSRF = True
    CACHE_TYPE = 'simple'

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir,'data-dev.db')

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  #   in memory database

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production':ProductionConfig
}
