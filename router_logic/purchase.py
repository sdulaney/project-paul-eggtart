from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField
from wtforms.validators import DataRequired
from wtforms import TextAreaField, TextField, validators
from wtforms.fields.html5 import IntegerField
import requests

class purchase_form(FlaskForm):
    card = StringField('card', [validators.Length(min=1, max=50)])
    little = BooleanField('little')

    def process_payment(self,card_num): # returns true/false based on whether credit card was successfully processed
        PARAMS = { 'card': card_num } 
          
        # Dummy API I created to verify credit cards (true if the length of the card is 16)
        r = requests.get(url = "https://yanggatang.pythonanywhere.com/verify_card", params = PARAMS) 

        if r.text == "False":#not verified
            return False
        else: #verified
            return True