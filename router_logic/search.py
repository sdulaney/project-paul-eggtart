from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, validators
from wtforms.validators import DataRequired
from fuzzywuzzy import fuzz, process
from TA_functions import *


def closest_match(search):
	choices = get_ta_list()
	return process.extract(search, choices, limit=1)

def closest_5_match(search):
	choices = get_ta_list()
	return [name[0] for name in process.extract(search, choices, limit=5)]

class searchBar(FlaskForm):
    ta_name = StringField('ta_name', [validators.Length(min=1, max=50)])
