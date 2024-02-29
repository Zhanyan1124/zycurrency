from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from flask_wtf.file import FileField, FileAllowed
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
    last_name = StringField('Last Name')
    
    nationality= QuerySelectField(query_factory=lambda: Country.query.all(),
                                    allow_blank=True, get_label="name")  
    default_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                    allow_blank=True, get_label=currency_label)  
    
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password',[validators.DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png'], 'Only images with jpg and pdf format are accepted')
    ])
    submit = SubmitField('Sign Up')


class EditProfileForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png'], 'Only images with jpg and pdf format are accepted')
    ])

    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name')
    
    nationality= QuerySelectField(query_factory=lambda: Country.query.all(),
                                    allow_blank=True, get_label="name")  
    default_cur= QuerySelectField(query_factory=lambda: Currency.query.all(),
                                    allow_blank=True, get_label=currency_label)  
    
    submit = SubmitField('Edit')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password')
    new_password = PasswordField(' NewPassword', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('new_password', message='Passwords must match')
    ])