import os
import pyrebase
from dotenv import load_dotenv
# LOAD ENVIRONMENT VARIABLES 
load_dotenv()
load_dotenv(verbose=True)
from pathlib import Path  
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
#LOAD ENVIRONMENT VARIABLES

config = {
  "apiKey": os.environ.get('FIREBASE_API_KEY'),
  "authDomain": "rate-my-ta.firebaseapp.com",
  "databaseURL": "https://rate-my-ta.firebaseio.com",
  "projectId": "rate-my-ta",
  "storageBucket": "rate-my-ta.appspot.com",
  "serviceAccount": "key/firebase-key.json",
  "messagingSenderId": "358133458427"
}
def database():
	firebase = pyrebase.initialize_app(config)
	db = firebase.database()
	return db

	