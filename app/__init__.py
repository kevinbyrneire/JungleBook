from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import os
app=Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
if os.environ.get('DATABASE_URL') is None:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = 'kevinsmagickey'
app.config['WHOOSH_BASE'] = os.path.join(basedir,'search.db')
app.config['MAX_SEARCH_RESULTS']= 50
MAX_USERS = 10
db=SQLAlchemy(app)
log_man = LoginManager()
log_man.init_app(app)
log_man.login_view = 'login'
from app import views,models
if __name__=='__main__':
	app.run()
