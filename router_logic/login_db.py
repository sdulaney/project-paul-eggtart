from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
    render_template
)
from flask_wtf import FlaskForm
from wtforms import Form, TextAreaField, StringField, validators
from wtforms.validators import DataRequired
from load import database
from profile.profile import User
import datetime
from datetime import timedelta

db = database()

class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()]) 

    def login(self, user):
        decrypter = User() # we need the decrypt function from the user
        users = db.child("users").get()
        
        for u in users.each():
            data = u.val()
            if data['email'] == user.email and decrypter.decrypt(data["password"],user.password): #data["password"] == user.password:
                last_lockout = data['last_lockout']
                last_lockout = datetime.datetime.strptime(last_lockout, '%Y-%m-%dT%H:%M:%S.%f')
                if last_lockout > datetime.datetime.now():
                    flash("Too many login attempts. Please try again in 5 minutes")
                    return -4
                if data['authenticated'] is False:
                    flash("Account not authenticated. Please reauthenticate.")
                    return -2
                reset_date = data['password_reset']
                reset_date_obj = datetime.datetime.strptime(reset_date, '%Y-%m-%dT%H:%M:%S.%f')
                if reset_date_obj < datetime.datetime.now():
                    flash("Password has expired. Please reset your password")
                    return -3
                id = data['id']
                db.child('users').child(id).update({"num_lockouts": 0})
                return int(data['id'])
            #incorrect password
            elif data['email'] == user.email:
                id = data['id']
                num_lockouts = data['num_lockouts']
                last_lockout = data['last_lockout']
                last_lockout = datetime.datetime.strptime(last_lockout, '%Y-%m-%dT%H:%M:%S.%f')
                num_lockouts += 1
                if last_lockout < datetime.datetime.now():
                    if num_lockouts % 5 == 0:
                        last_lockout = datetime.datetime.now() + timedelta(minutes=5)
                        last_lockout = last_lockout.isoformat()
                        flash("Too many login attempts. Please try again in 5 minutes")
                        db.child('users').child(id).update({"num_lockouts": num_lockouts, "last_lockout": last_lockout})
                        return -4
                    else:
                        db.child('users').child(id).update({"num_lockouts": num_lockouts})
                        return -1
                else:
                    flash("Too many login attempts. Please try again in 5 minutes")
                    return -2
        return -1