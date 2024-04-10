from apps import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name =  db.Column(db.String(150))
    last_name =  db.Column(db.String(150))
    picture_url = db.Column(db.String(255))
    fav_curs = db.Column(db.String(255))
    nationality = db.Column(db.String(3), db.ForeignKey('country.code'), nullable=True)
    default_cur = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=True)
    second_cur = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=True)

    currency = relationship('Currency', foreign_keys=[default_cur], backref='users_default', uselist=False)
    second_currency = relationship('Currency', foreign_keys=[second_cur], backref='users_second', uselist=False)
    country = relationship('Country', backref='users')