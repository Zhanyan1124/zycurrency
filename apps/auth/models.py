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
    nationality = db.Column(db.String(3), db.ForeignKey('country.code'), nullable=True)
    default_cur = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=True)

    currency = relationship('Currency', backref='users')
    country = relationship('Country', backref='users')