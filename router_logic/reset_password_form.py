from flask import (
    current_app,
    Blueprint,
    request,
    redirect,
    url_for,
    jsonify,
    render_template
)
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import validators, PasswordField
from load import database
from profile.profile import User
from itsdangerous import URLSafeTimedSerializer

class PasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])

