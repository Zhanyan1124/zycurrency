from apps import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    alert_type = db.Column(db.String(13), nullable = False)
    period = db.Column(db.String(5))
    condition = db.Column(db.String(4))
    rate = db.Column(db.Float)
    notify_in_app = db.Column(db.Boolean)
    notify_email = db.Column(db.Boolean)
    notes = db.Column(db.String(255))
    is_enabled = db.Column(db.Boolean)
    from_cur_code = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False, index=True, unique=False)
    to_cur_code = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False, index=True, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True, unique=False)
    
    from_cur = db.relationship('Currency', foreign_keys=[from_cur_code])
    to_cur = db.relationship('Currency', foreign_keys=[to_cur_code])
    user = db.relationship('User',foreign_keys=[user_id])