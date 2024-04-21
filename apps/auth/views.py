from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignUpForm, LoginForm, EditProfileForm, ChangePasswordForm, ForgetPasswordForm, ResetPasswordForm, AddProfileForm
from .models import User
from .exceptions import EmailExistedException, InvalidPasswordException
import os
import requests
import json
from oauthlib.oauth2 import WebApplicationClient
from flask_mail import Message
from werkzeug.utils import secure_filename
from apps import db
from apps import mail
from apps.models import Currency, Country
from .tasks import send_reset_password_mail, send_verify_account_mail
from itsdangerous import SignatureExpired, BadSignature 

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.password is None:
            flash('This account does not have password', 'danger')

        elif user and user.email_verified and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('views.home'))
        else:
            if user and not user.email_verified:
                flash('This account has not been verified. Please check your inbox.', 'danger')
            else:
                flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    currencies = Currency.query.all()
    countries = Country.query.all()
    fav_curs_codes = [currency.code for currency in form.fav_curs.data] if form.fav_curs.data else None
    try:
        if request.method == 'POST' and form.validate_on_submit():
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                raise EmailExistedException('This email address is already registered.')
            
            if form.profile_picture.data:
                profile_picture = form.profile_picture.data
                filename = secure_filename(profile_picture.filename)
                folder_path = os.path.join(current_app.root_path, 'static', 'user_pics')
                file_path = os.path.join(folder_path, filename)
                profile_picture.save(file_path)
                picture_url = 'user_pics/' + filename
            else:
                picture_url = None
            
            
            default_cur = form.default_cur.data.code
            if form.second_cur.data:
                second_cur = form.second_cur.data.code
                if default_cur == second_cur: 
                    raise Exception("Default currency cannot be the same with your second currency")
            else:
                if default_cur!= "USD":
                    second_cur = "USD"
                else:
                    second_cur = "EUR"

            email = form.email.data
            hashed_password = generate_password_hash(form.password.data, method='scrypt')
            first_name = form.first_name.data
            nationality = form.nationality.data.code if form.nationality.data else None
            last_name = form.last_name.data if form.last_name.data else None
            fav_curs = ','.join(currency.code for currency in form.fav_curs.data) if form.fav_curs.data else None
            new_user = User(email=email, password=hashed_password, first_name = first_name, last_name = last_name, default_cur = default_cur, second_cur = second_cur, fav_curs = fav_curs, nationality = nationality, picture_url=picture_url)
            db.session.add(new_user)
            db.session.commit()

            serializer = current_app.config['SERIALIZER']
            token = serializer.dumps(email, salt='verify-account')
            verify_account_url = current_app.config['URL_DOMAIN_WITH_PROTOCOL'] + url_for('auth.verify_account', token=token, external=True)
            html_template = render_template('mails/verify_account_mail.html', verify_account_url=verify_account_url)
            send_verify_account_mail.delay(email, html_template)  
            flash('Sign up successful. You may check your email inbox to verify your account.', 'success')
            return redirect(url_for('auth.login'))
        
        elif request.method == 'POST' and not form.validate_on_submit():
            form.populate_obj(request.form)

    except EmailExistedException as e:
        flash(str(e), 'danger')
    
    except Exception as e:
        flash(f'Error during sign up: {str(e)}', 'danger')

    return render_template('sign_up.html', form=form, currencies=currencies, countries=countries, fav_curs_codes = fav_curs_codes)

@auth_bp.route('/verify-account/<token>', methods=['GET'])
def verify_account(token):
    serializer = current_app.config['SERIALIZER']
    try:
        email = serializer.loads(token, salt='verify-account', max_age=1800)
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_verified = True
            db.session.commit()
            flash('Your account has been verified. You can proceed to log in to the system.', 'success')
            return redirect(url_for('auth.login'))
        else:
            abort(404) 
    except SignatureExpired:
        flash('Verification link has expired. Please sign up again.', 'danger')
        return redirect(url_for('auth.login'))

    except BadSignature:
        abort(404) 


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordForm()
    try:
        if request.method == 'POST' and form.validate_on_submit():
            form.populate_obj(request.form)
            email = form.email.data
            serializer = current_app.config['SERIALIZER']
            token = serializer.dumps(email, salt='reset-password')
            
            reset_password_url = current_app.config['URL_DOMAIN_WITH_PROTOCOL'] + url_for('auth.reset_password', token=token, external=True)
            html_template = render_template('mails/reset_password_mail.html', reset_password_url=reset_password_url)
            send_reset_password_mail.delay(email, html_template)
            flash('Please check your email inbox to reset your password.', 'success')

    except Exception as e:
        flash(f'Error when sending reset password email: {str(e)}', 'danger')

    return render_template('forget_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    serializer = current_app.config['SERIALIZER']
    try:
        email = serializer.loads(token, salt='reset-password', max_age=1800)
    except Exception as e:
        abort(404)
    
    form.email.data = email
    try:
        if request.method == 'POST' and form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if(check_password_hash(user.password, form.password.data)):
                raise InvalidPasswordException ('You are using an old password')
            hashed_password = generate_password_hash(form.password.data, method='scrypt')
            user.password = hashed_password
            db.session.commit()
            flash('Password has been reset. You may proceed to login now.', 'success')
    except InvalidPasswordException as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error when changing password: {str(e)}', 'danger')
    return render_template('reset_password.html', form=form, email=email)


@auth_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    currencies = Currency.query.all()
    countries = Country.query.all()

    try:
        if request.method == 'POST' and form.validate_on_submit():
            first_name = form.first_name.data
            nationality = form.nationality.data.code if form.nationality.data else None
            last_name = form.last_name.data if form.last_name.data else None
            default_cur = form.default_cur.data.code if form.default_cur.data else None
            second_cur = form.second_cur.data.code if form.second_cur.data else None
            if default_cur == second_cur:
                raise Exception("Default currency cannot be the same with your second currency") 
            fav_curs = ','.join(currency.code for currency in form.fav_curs.data) if form.fav_curs.data else None
            
            if form.profile_picture.data:
                profile_picture = form.profile_picture.data
                filename = secure_filename(profile_picture.filename)
                folder_path = os.path.join(current_app.root_path, 'static', 'user_pics')
                file_path = os.path.join(folder_path, filename)
                profile_picture.save(file_path)
                current_user.picture_url = 'user_pics/' + filename

            current_user.first_name = form.first_name.data
            current_user.last_name = last_name
            current_user.nationality = nationality
            current_user.default_cur = default_cur
            current_user.second_cur = second_cur
            current_user.fav_curs = fav_curs

            db.session.commit()

            flash('Edited profile successfully.', 'success')
        
        elif request.method == 'POST' and not form.validate_on_submit():
            form.populate_obj(request.form)
    
    except Exception as e:
        flash(f'Error when editing profile: {str(e)}', 'danger')

    return render_template('edit_profile.html', form=form, current_user=current_user, currencies=currencies, countries=countries)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    try:
        if request.method == 'POST' and form.validate_on_submit():
            if(current_user.password):
                if(form.old_password.data == None):
                    raise InvalidPasswordException ('Old password is required for validation.')
                if(check_password_hash(current_user.password, form.old_password.data) == False):
                    raise InvalidPasswordException ('The old password does not match with existing password.')
                if(check_password_hash(current_user.password, form.new_password.data)):
                    raise InvalidPasswordException ('You are using an old password')
            hashed_password = generate_password_hash(form.new_password.data, method='scrypt')
            current_user.password = hashed_password
            db.session.commit()

            flash('Changed password successfully.', 'success')

    except InvalidPasswordException as e:
        flash(str(e), 'danger')
    
    except Exception as e:
        flash(f'Error when changing password: {str(e)}', 'danger')
            
    return render_template('change_password.html', form=form)



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
        first_name=first_name, last_name=last_name, email=email, picture_url= picture_url, email_verified= True
    )
    
    existing_user = User.query.filter_by(email=user.email).first()

    if not existing_user:
        db.session.add(user)
        db.session.commit()
    else:
        user = existing_user

    login_user(user)
    if not current_user.default_cur:
        return redirect(url_for("auth.add_profile"))
    else:
        return redirect(url_for("views.home"))

@auth_bp.route('/add-profile', methods=['GET', 'POST'])
@login_required
def add_profile():
    form = AddProfileForm()
    currencies = Currency.query.all()
    countries = Country.query.all()

    if current_user.default_cur:
        return redirect(url_for("views.home"))

    try:
        if request.method == 'POST' and form.validate_on_submit():
            nationality = form.nationality.data.code if form.nationality.data else None
            default_cur = form.default_cur.data.code if form.default_cur.data else None
            second_cur = form.second_cur.data.code if form.second_cur.data else None
            if default_cur == second_cur:
                raise Exception("Default currency cannot be the same with your second currency") 
            fav_curs = ','.join(currency.code for currency in form.fav_curs.data) if form.fav_curs.data else None
            
            current_user.nationality = nationality
            current_user.default_cur = default_cur
            current_user.second_cur = second_cur
            current_user.fav_curs = fav_curs

            db.session.commit()
            return redirect(url_for("views.home"))
        
        elif request.method == 'POST' and not form.validate_on_submit():
            form.populate_obj(request.form)
    
    except Exception as e:
        flash(f'Error when adding profile: {str(e)}', 'danger')

    return render_template('add_profile.html', form=form, current_user=current_user, currencies=currencies, countries=countries)


def get_google_provider_cfg(url):
    return requests.get(url).json()

def get_google_credentials():
    with current_app.app_context():
        client_id = current_app.config["GOOGLE_CLIENT_ID"]
        client_secret = current_app.config["GOOGLE_CLIENT_SECRET"]
        google_url = current_app.config["GOOGLE_DISCOVERY_URL"]

        return (client_id, client_secret, google_url)



