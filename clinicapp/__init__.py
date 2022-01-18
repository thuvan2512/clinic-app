from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = '@pdot324g942##$%$^$@%#%^%$^*&*(&)(3jifgj34-94'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:25122k@localhost/clinicapp?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
login = LoginManager(app=app)
cloudinary.config(
    cloud_name = 'dec25',
    api_key = '752682513512722',
    api_secret = 'P6Sb5YZCvBFpcMYAyumZnIpewNU'
)
db = SQLAlchemy(app=app)
