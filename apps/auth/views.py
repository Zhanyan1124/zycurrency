from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignUpForm, LoginForm
from .models import User
from .exceptions import EmailExistedException
import os
import requests
import json
from oauthlib.oauth2 import WebApplicationClient

from apps import db



auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.password is None:
            flash('This account does not have password', 'danger')

        elif user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form, signup_url=url_for('auth.signup'), google_login_url=url_for('auth.google_login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    
    try:
        if request.method == 'POST' and form.validate_on_submit():
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                raise EmailExistedException('This email address is already registered.')
            
            hashed_password = generate_password_hash(form.password.data, method='scrypt')
            new_user = User(email=form.email.data, password=hashed_password, first_name = form.first_name.data, last_name = form.last_name.data, default_cur = form.default_cur.data.code, nationality = form.nationality.data.code)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Sign up successful. You may proceed to log in.', 'success')
            return redirect(url_for('auth.login'))
        
        elif request.method == 'POST' and not form.validate_on_submit():
            form.populate_obj(request.form)

    except EmailExistedException as e:
        flash(str(e), 'danger')
    
    except Exception as e:
        flash(f'Error during sign up: {str(e)}', 'danger')

    return render_template('sign_up.html', form=form, login_url=url_for('auth.login'))



@auth_bp.route('/google_login')
def google_login():
    client_id, client_secret, google_url = get_google_credentials()
    client = WebApplicationClient(client_id)   
    google_provider_cfg = get_google_provider_cfg(google_url)
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["email", "profile"],
    )
    return redirect(request_uri)


@auth_bp.route('/google_login/callback')
def google_login_callback():
    client_id, client_secret, google_url = get_google_credentials()
    client = WebApplicationClient(client_id)  
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg(google_url)
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(client_id, client_secret),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        picture_url = userinfo_response.json()["picture"]
        first_name = userinfo_response.json()["given_name"]
        if userinfo_response.json().get("family_name"):
            last_name = userinfo_response.json()["family_name"]
        else:
            last_name= None
        
    else:
        return "User email not available or not verified by Google.", 500

    user = User(
        first_name=first_name, last_name=last_name, email=email, picture_url= picture_url
    )
    
    existing_user = User.query.filter_by(email=user.email).first()

    if not existing_user:
        db.session.add(user)
        db.session.commit()
    else:
        user = existing_user

    login_user(user)
    return redirect(url_for("views.home"))


def get_google_provider_cfg(url):
    return requests.get(url).json()

def get_google_credentials():
    with current_app.app_context():
        client_id = current_app.config["GOOGLE_CLIENT_ID"]
        client_secret = current_app.config["GOOGLE_CLIENT_SECRET"]
        google_url = current_app.config["GOOGLE_DISCOVERY_URL"]

        return (client_id, client_secret, google_url)