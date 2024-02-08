from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from .forms import ConvertForm
from flask_login import login_required, current_user
import requests

currency_bp = Blueprint('currency', __name__, template_folder='templates')

@currency_bp.route('/convert', methods=['GET', 'POST'])
@login_required
def convert():
    form = ConvertForm()

    exchange_rate=None
    convert_result=None
    if request.method == 'POST' and form.validate_on_submit():
        headers = {"accept": "application/json"}
        convert_url = "{}/convert?api_key={}&from={}&to={}&amount={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], form.from_cur.data.code, form.to_cur.data.code, form.amount.data)
        print(convert_url)
        response = requests.get(convert_url, headers=headers)
        
        if response.status_code == 200:
            json_obj = response.json()  
            print(json_obj)
            base= json_obj['base']
            result= json_obj['result']
            print('Base: ', base)
            print(result)
            exchange_rate = result['rate']
            convert_result = result[form.to_cur.data.code]
            print("Exchange rate:", exchange_rate)
            print("Converted result:", convert_result)
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
    return render_template('convert.html', form=form, user=current_user, exchange_rate=exchange_rate, convert_result=convert_result)