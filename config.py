import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    dbmysql = "vamostrabalhar"
    usermysql = "admin"
    senhamysql = "S3nhaADMIN#"
    hostmysql = "127.0.0.1"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+usermysql+':'+senhamysql+'@'+hostmysql+'/'+dbmysql
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'uploads') # you'll need to create a folder named upload
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'contato.vtj@gmail.com'
    MAIL_PASSWORD = 'Rtdqxj00'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Vamos Trabalhar Juntos]'
    FLASKY_MAIL_SENDER = 'contato.vtj@gmail.com'
    FLASKY_ADMIN = 'contato.vtj@gmail.com'   
    
