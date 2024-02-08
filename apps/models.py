from apps import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Country(db.Model):
    code = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String(150), unique = True, nullable = False)
    flag = db.Column(db.String(5))
    currency_code = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False, index=True, unique=False)

    currency = relationship('Currency', backref='countries')

class Currency(db.Model):
    code = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String(150), unique = True, nullable = False)