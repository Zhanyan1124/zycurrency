from flask_seeder import Seeder
from apps.models import Currency
from apps import db
from flask import current_app 
import json
import requests

class CurrencySeeder(Seeder):
  def __init__(self, db=None):
    super().__init__(db=db)
    self.priority = 1

  def run(self):
    if db.session.query(Currency).first() is None:
      print('Adding Currency Seeder ... ') 
      url = "{}/currencies?api_key={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'])
      headers = {"accept": "application/json"}
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
        json_obj = response.json()  
        currencies= json_obj['currencies']
        for code, name in zip(currencies.keys(), currencies.values()):
            currency = Currency(code=code, name=name)
            db.session.add(currency)
        db.session.commit()
             
      else:
          print(f"Error: {response.status_code} - {response.text}")
    else:
      print('Skipping Currency Seeder ... ')
