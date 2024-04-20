from apps import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Country(db.Model):
    code = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String(150), unique = True, nullable = False)
    currency_code = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False, index=True, unique=False)

    currency = relationship('Currency', backref='countries')

class Currency(db.Model):
    code = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String(150), unique = True, nullable = False)
    alpha_2_code = db.Column(db.String(2))