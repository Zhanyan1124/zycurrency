from apps import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    created_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    text = db.Column(db.String(255))
    has_read = db.Column(db.Boolean)
    alert_id = db.Column(db.Integer, db.ForeignKey('alert.id'), nullable=True, index=True, unique=False)
    
    alert = db.relationship('Alert',foreign_keys=[alert_id])