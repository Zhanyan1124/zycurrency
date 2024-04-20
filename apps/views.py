from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_login import login_required, current_user
from .models import Currency

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    if not current_user.default_cur:
        return redirect(url_for("auth.add_profile"))
    from_cur = current_user.default_cur
    to_cur=current_user.second_cur
    currencies = Currency.query.all()
    popular_curs = current_app.config["POPULAR_CURRENCIES"]
    fav_curs = None
    if current_user.fav_curs:
        fav_curs = current_user.fav_curs.split(',')
        if from_cur in fav_curs:
            fav_curs.remove(from_cur)
    if from_cur in popular_curs:
        popular_curs.remove(from_cur)

        
    return render_template("home.html", user=current_user, currencies=currencies, from_cur=from_cur, to_cur=to_cur, popular_curs = popular_curs, fav_curs = fav_curs)