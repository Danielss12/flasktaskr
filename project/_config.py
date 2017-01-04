import os

basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE ='flasktaskr.db'
WTF_CSRF_ENABLED = True
SECRET_KEY = '\xd7\xad\xf1\xe7\xbe\xa2\xdb\xa5N`\x16\x14\xfc\x94\x999\xc5\xbdtr\xbf\xec\r\xd9'
DEBUG = True
DATABASE_PATH =	os.path.join(basedir, DATABASE)

#database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH