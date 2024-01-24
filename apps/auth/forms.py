from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators


class LoginForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Invalid email address')
    ])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message='Invalid email address')
    ])
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password',[validators.DataRequired()])
    submit = SubmitField('Sign Up')
