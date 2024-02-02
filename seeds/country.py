from flask_seeder import Seeder
from apps.models import Country
from apps import db
import pycountry 

class CountrySeeder(Seeder):

  def run(self):
    if db.session.query(Country).first() is None:
      print('Adding Country Seeder ... ')
      all_countries = list(pycountry.countries)
      for country in all_countries:
        print(f"Name: {country.name}, Alpha-2 code: {country.alpha_2}, Alpha-3 code: {country.alpha_3}")
        print(f"Flag: {country.flag}")
        new_country = Country(name=country.name, code=country.alpha_3, flag=country.flag)
        db.session.add(new_country)
      db.session.commit()

    else:
      print('Skipping Country Seeder ... ')
