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

