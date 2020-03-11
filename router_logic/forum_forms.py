from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms import TextAreaField, TextField, validators
from wtforms.fields.html5 import IntegerField

class comment_form(FlaskForm):
    comment = StringField('comment', validators=[DataRequired()])

class rating_form(FlaskForm):
    clarity = IntegerField('clarity', default=3)
    helpfulness = IntegerField('helpfulness', default=3)
    availability = IntegerField('availability', default=3)