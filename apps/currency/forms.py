from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, BooleanField, RadioField, validators, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from apps.models import Currency


from wtforms.validators import DataRequired


class ConvertForm(FlaskForm):
    amount = DecimalField('Amount',  [validators.DataRequired()])
    from_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                allow_blank=False)  
    to_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                allow_blank=False) 
    submit = SubmitField('Convert')

def get_duration_choices():
    return [('7d', 'One week'), ('14d', 'Two weeks'), ('1m', 'One month'), ('3m','Three months'), ('6m','Six months'), ('1y', 'One year'), ('2y', 'Two years')]

class HistoricalRateChangesForm(FlaskForm):
    from_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                allow_blank=False)  
    to_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                allow_blank=False) 
    duration = SelectField('Duration', choices=get_duration_choices())
    submit_convert = SubmitField('View')

class CreateExRateNotificationForm(FlaskForm):
    from_cur= StringField('From Currency') 
    to_cur= StringField('To Currency')
    alert_type = RadioField('Alert Type', choices=[('periodically', 'Periodically'), ('conditionally', 'Conditionally')])
    period = SelectField('Period', choices=[('day', 'Each Day'),('week', 'Each Week'),('month', 'Each Month')])
    condition = SelectField('Condition', choices=[('more', 'More Than (>)'),('less', 'Less Than (<)')])
    rate = DecimalField('Rate')
    notify_in_app = BooleanField('In-App')
    notify_email = BooleanField('Email')
    notes = StringField('Notes')
    submit_notification = SubmitField('Set')