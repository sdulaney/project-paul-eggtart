import datetime
import json
import re
from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template
)
from load import database
from flask_wtf import FlaskForm
from wtforms import Form, TextAreaField, TextField, StringField, BooleanField, DateTimeField, FieldList, SubmitField, validators
from wtforms.validators import DataRequired
from wtforms.fields.html5 import IntegerField
from flask_login import UserMixin, current_user
# ----- password db encryption portion
import bcrypt


db = database()

class User(UserMixin):
    id = IntegerField('id')
    email = StringField('email', validators=[DataRequired()])
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    authenticated = BooleanField('authenticated', default=False)
    password_reset = DateTimeField('password_reset')
    num_lockouts = IntegerField('num_lockouts', default=0)
    last_lockout = DateTimeField('last_lockout')
    credits = IntegerField('credits', default=0)
    viewable_ta = FieldList('ta_name', StringField())
    remaining_views = IntegerField('remaining_views', default=3)

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False

    def __init__(self):
        return
    
    def get_id(self):
        try:
            user_list = db.child('users').get()
            for i in user_list.each():
                if(i.val() is not None):
                    if self.email == (i.val()["email"]): #return the id associated with this email
                        return i.val()["id"]
        except AttributeError:
            raise NotImplementedError("No id found")

    def get(self, id):
        try:
            return User
        except:
            return None

    def model_class(self):
        return User

    def get_user(self, db, username):
        user = db.child('users').child(username).get()
        data = user.val()
        for key, val in user.val().items():
            setattr(self, key, val)

        ta_list = []
        for ta in self.viewable_ta:
            ta_list.append(str(data["viewable_ta"][ta]['name']))

        return self, ta_list
    
    def update_user(self, form, **kwargs):
        cls = self.model_class()
        
        names = self.get_properties()
        attributes = self.validate_data(names, form)
        id = attributes["id"]
        current_user,_ = self.get_user(db, id)
        attributes["retype_password"] = form.get("retype_password")
        for key, val in list(attributes.items()):
            if val == '':
                del attributes[key]
        reset_password = False
        if "password" in attributes:
            reset_password = True
            if "retype_password" in attributes:
                if attributes["password"] != attributes["retype_password"]:
                    flash("Updated passwords do not match")
                    return "Fail"
                if not re.match("^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$", attributes["password"]):
                    flash("Password must have at least one letter, one number, one special character, and be at least 8 characters long")
                    return "Fail"
        if reset_password:
            if self.decrypt(current_user.password, attributes["password"]):
                flash("Password cannot match old password")
                return "Fail"
            del attributes["retype_password"] 

            attributes["password"] = self.encrypt(attributes["password"])
            self.update_password_reset(id)
        db.child('users').child(id).update(attributes)
        return "Success"

    def get_parameters(self):
        cls = self.model_class()
        parameters = []
        for name in cls.__dict__.keys():
            if hasattr(User, name) and not name.startswith('_') and not callable(getattr(User, name)):
                parameters.append({
                    "name": name
                })
        return parameters

    #returns array of properties
    def get_properties(self):
        cls = self.model_class()
        names = []
        for name in cls.__dict__.keys():
            if hasattr(User, name) and not name.startswith('_') and not callable(getattr(User, name)):
                names.append(name)
        return names

    def validate_data(self, names, params):
        attributes = {}
        for name in names:
            param = params.get(name)
            if param is not None:
                if hasattr(User, name):
                    attributes[name] = param
        return attributes

    # Return number of views left to user, return None if no user exists
    def number_views(self):
        current_session_user = db.child('users').child(current_user.id).get().val()
        if current_session_user is not None:
            num_views = current_session_user['remaining_views']
            return num_views
        else:
            return None

    def update_password_reset(self, id):
        reset_date_time = (datetime.datetime.now() + datetime.timedelta(6*365/12)).isoformat()
        db.child('users').child(id).update({"password_reset": reset_date_time})
    
    # Return whether the TA is viewable or not
    def ta_viewable(self, ta_name):
        ta_viewable_list = db.child('users').child(current_user.id).child('viewable_ta').get()

        for _, val in ta_viewable_list.val().items():
            if val['name'] == ta_name:
                return True
        return False

    # decrement views if they need to be
    def handle_viewlist(self, ta_name):
        current_session_user = db.child('users').child(current_user.id).get().val()
        if self.ta_viewable(ta_name):
            return False

        # update db with decremented number of views
        current_session_user['remaining_views'] = current_session_user['remaining_views'] - 1
        db.child('users').child(current_user.id).update(current_session_user)
        # add new TA to the viewables list
        db.child('users').child(current_user.id).child('viewable_ta').push({'name': ta_name, 'rated': False})
        return True

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def encrypt(self,password_plain):
        passwd = password_plain.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(passwd, salt)
        # hashed password converted to string
        return hashed.decode('utf-8')

    def decrypt(self,password_hashed,password_plain):
        if bcrypt.checkpw(password_plain.encode('utf-8'), password_hashed.encode('utf-8')):
            return True
        return False
