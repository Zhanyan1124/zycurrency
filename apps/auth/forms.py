from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms_sqlalchemy.fields import QuerySelectField
from apps.models import Country, Currency
from markupsafe import Markup

class LoginForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Invalid email address')
    ])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Login')

def currency_label(currency):
    return currency.code + ' - ' + currency.name

class SignUpForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Invalid email address')
    ])
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    
    nationality= QuerySelectField(query_factory=lambda: Country.query.all(),
                                    allow_blank=True, get_label="name")  
    default_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                    allow_blank=True, get_label=currency_label)  
    
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password',[validators.DataRequired()])
    submit = SubmitField('Sign Up')
