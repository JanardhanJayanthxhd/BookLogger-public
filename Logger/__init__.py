from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.app_context().push()

# crypter
bcrypt = Bcrypt(app)

# User manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Database
db = SQLAlchemy(app)

from Logger import routes
