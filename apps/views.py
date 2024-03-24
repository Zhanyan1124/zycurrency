from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from .models import Currency

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    from_cur = current_user.default_cur
    to_cur='USD'
    currencies = Currency.query.all()
    popular_curs = current_app.config["POPULAR_CURRENCIES"]
    if from_cur in popular_curs:
        popular_curs.remove(from_cur)
        
    return render_template("home.html", user=current_user, currencies=currencies, from_cur=from_cur, to_cur=to_cur, popular_curs = popular_curs)