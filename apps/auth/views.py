from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignUpForm, LoginForm
from .models import User
from .exceptions import EmailExistedException

from apps import db

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form, signup_url=url_for('auth.signup'))

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
            new_user = User(email=form.email.data, password=hashed_password, first_name = form.first_name.data, last_name = form.last_name.data)
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
