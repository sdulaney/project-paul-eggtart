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
from wtforms import TextAreaField, StringField, validators
from wtforms.validators import DataRequired
from load import database
from profile.profile import User
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from extensions import mail

class EmailForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])

def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = ""
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user_email):
    password_reset_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    password_reset_url = url_for(
        'router.reset_with_token',
        token = password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)

    html = render_template(
        'email_password_reset.html',
        password_reset_url=password_reset_url)

    send_email('Password Reset Requested', [user_email], html)
