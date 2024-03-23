from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Currency

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    from_cur=None
    to_cur='USD'
    currencies = Currency.query.all()

    if current_user.default_cur != None:
        from_cur = current_user.default_cur
    return render_template("home.html", user=current_user, currencies=currencies, from_cur=from_cur, to_cur=to_cur)