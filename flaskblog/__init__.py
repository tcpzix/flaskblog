from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '0312a2e2a0a4fcac8d99c4509a838'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# to tell the extention(flask_login) where is login route is located (for using login_required)
login_manager.login_view = 'login'
# for change category of login required message(please login to access that page) in bootstrap
login_manager.login_message_category = 'alert'

from flaskblog import routes