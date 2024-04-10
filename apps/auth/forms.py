from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, SelectMultipleField, EmailField
from flask_wtf.file import FileField, FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo
from apps.models import Country, Currency
from markupsafe import Markup


class LoginForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Invalid email address')
    ])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Login')


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(message='Invalid email address')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name')
    nationality = QuerySelectField(query_factory=lambda: Country.query.all(), allow_blank=True, get_label="name")  
    default_cur = QuerySelectField(query_factory=lambda: Currency.query.all(), allow_blank=False)  
    second_cur = QuerySelectField(query_factory=lambda: Currency.query.all(), allow_blank=True) 
    fav_curs = QuerySelectMultipleField(query_factory=lambda: Currency.query.all(), allow_blank=True)
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Only images with jpg and pdf format are accepted')])
    submit = SubmitField('Sign Up')




class EditProfileForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png'], 'Only images with jpg and pdf format are accepted')
    ])
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name')
    nationality = QuerySelectField(query_factory=lambda: Country.query.all(), allow_blank=True, get_label="name")  
    default_cur = QuerySelectField(query_factory=lambda: Currency.query.all(), allow_blank=False)  
    second_cur = QuerySelectField(query_factory=lambda: Currency.query.all(), allow_blank=False) 
    fav_curs = QuerySelectMultipleField(query_factory=lambda: Currency.query.all(), allow_blank=True)  
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

class ForgetPasswordForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Invalid email address')
    ])

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Invalid email address')
    ])
    password = PasswordField(' Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])