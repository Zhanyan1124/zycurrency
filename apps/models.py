from apps import db

class Country(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), unique = True, nullable = False)
    code = db.Column(db.String(3), unique = True, nullable = False)
    flag = db.Column(db.String(5))
