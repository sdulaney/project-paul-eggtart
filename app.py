import os
from flask_login import LoginManager, login_manager
from flask import (
    Flask,
    Blueprint,
    redirect,
    url_for
)
from extensions import mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address # limiter against DDOS
from router.router import router
from flask_wtf.csrf import CSRFProtect
from profile.profile import User
from flask_mail import Mail, Message
import load



login_manager = LoginManager()

csp = {
    'default-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'stackpath.bootstrapcdn.com',
        'code.jquery.com',
        'cdn.jsdelivr.net',
        'https://rate-my-ta.herokuapp.com/',
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com/icon?family=Material+Icons',
        'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js',
        'https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
        'http://farm8.staticflickr.com/7064/6858179818_5d652f531c_h.jpg',
        'https://fonts.googleapis.com/css?family=Open+Sans+Condensed:300,700|Open+Sans:400,300,600',
        'https://fonts.googleapis.com/icon?family=Material+Icons',
        'https://fonts.gstatic.com/s/materialicons/v48/flUhRq6tzZclQEJ-Vdg-IuiaDsNcIhQ8tQ.woff2',
        '*'
    ],
    'img-src': '*',
    'script-src':'*',
    'style-src':'*',
    'font-src':'*'


}

def create_app(config_file):
    app = Flask(__name__)
    app.config.from_object(config_file)
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    csrf = CSRFProtect(app)
    csrf = CSRFProtect()
    app.config['SECRET_KEY'] = os.environ.get("CSRF_KEY_SECRET")
    app.secret_key = b'\x06\x82\x96n\xfa\xbb(L\x97n\xb8.c\\y\x8a'
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    app.register_blueprint(router, url='/router')
    css = Blueprint(
        'css',
        __name__,
        template_folder='templates',
        static_folder='static/css',
        static_url_path='/static/css'
    )
    js = Blueprint(
        'js',
        __name__,
        template_folder='templates',
        static_folder='static/js',
        static_url_path='/static/js'
    )
    app.register_blueprint(js)

    return app

app = create_app('config')

db = load.database()
limiter = Limiter(app,key_func=get_remote_address,default_limits=["20 per minute", "10 per second"])

@login_manager.user_loader
def load_user(user_id):
    user_data = db.child("users").child(user_id).get()
    if user_data.val() is None:
        return None
    user = User()
    user.id = user_data.val()["id"]
    user.email = user_data.val()["email"]
    return user


@login_manager.user_loader
def load_user(user_id):
    user_data = db.child("users").child(user_id).get()
    if user_data.val() is None:
        return None
    user = User()
    user.id = user_data.val()["id"]
    user.email = user_data.val()["email"]
    return user

@app.route('/')
def index():
    return redirect(url_for('router.home'))

@app.after_request
def add_header(response):
    response.headers["Cache_Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.set_cookie('username', 'flask', secure=True, httponly=True, samesite='Lax')
    return response

if __name__ == '__main__':
    app.run()