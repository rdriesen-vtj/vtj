import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    dbmysql = "vamostrabalhar02"
    usermysql = "vamostrabalhar02"
    senhamysql = "SenhaVTJ01"
    hostmysql = "mysql.vamostrabalharjuntos.com.br"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+usermysql+':'+senhamysql+'@'+hostmysql+'/'+dbmysql
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

