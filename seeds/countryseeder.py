from flask_seeder import Seeder
from apps.models import Country, Currency
from apps.database import db
import pycountry 
from countryinfo import CountryInfo

class CountrySeeder(Seeder):
  def __init__(self, db=None):
    super().__init__(db=db)
    self.priority = 2

  def run(self):
    db.session.query(Country).delete()
    db.session.commit()
    if db.session.query(Country).first() is None:
      print('Adding Country Seeder ... ') 
      all_countries = list(pycountry.countries)
      db.session.rollback()
      with db.session.begin():
        try:
          for country in all_countries:
            try:
              with db.session.no_autoflush:
                country_found = CountryInfo(country.name)
                if(country_found):
                  currencies = country_found.currencies()
                  currency = currencies[0]
                  if db.session.query(Currency).filter_by(code=currency).first():
                    new_country = Country(code=country.alpha_3, name=country.name, currency_code=currency)
                    db.session.add(new_country)
            except Exception as e:
                print(f"Error processing {country.name}: {e}")
                
        except Exception as outer_exception:
          print(f"Error: {outer_exception}")
          db.session.rollback()
              
    else:
      print('Skipping Country Seeder ... ')
