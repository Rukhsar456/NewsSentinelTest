import os
from flask import Flask, abort, jsonify, request, render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

import joblib
# import pickle
from news_sentinel.feature import *
import json
from nltk.corpus import stopwords

stop_words = stopwords.words('english')
from nltk.tokenize import word_tokenize

lemmatizer = WordNetLemmatizer()
nltk.download('wordnet')
pipeline = joblib.load('news_sentinel/pipeline.sav')

app = Flask(__name__)
app.config['SECRET_KEY'] = '1a9064468e3a50c4ba7e62728c804bac'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# email configs
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'newssentinel2@gmail.com'
app.config['MAIL_PASSWORD'] = 'newsSentinel123'
mail = Mail(app)

from news_sentinel import routes
