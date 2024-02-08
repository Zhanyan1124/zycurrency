from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, validators
from wtforms_sqlalchemy.fields import QuerySelectField
from apps.models import Currency

from wtforms.validators import DataRequired

def currency_label(currency):
    return currency.code + ' - ' + currency.name

class ConvertForm(FlaskForm):
    amount = DecimalField('Amount',  [validators.DataRequired()])
    from_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                allow_blank=False, get_label=currency_label)  
    to_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                allow_blank=False, get_label=currency_label) 
    submit = SubmitField('Convert')