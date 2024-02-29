from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, validators, SelectField
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
    submit = SubmitField('View')

