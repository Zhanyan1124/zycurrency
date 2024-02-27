from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from .forms import ConvertForm, HistoricalRateChangesForm
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
from apps.models import Currency

currency_bp = Blueprint('currency', __name__, template_folder='templates')

@currency_bp.route('/convert', methods=['GET', 'POST'])
@login_required
def convert():
    form = ConvertForm()
    exchange_rate=None
    convert_result=None
    from_cur=None
    to_cur='USD'

    currencies = Currency.query.all()
    if current_user.default_cur != None:
        from_cur = current_user.default_cur

    if request.method == 'POST' and form.validate_on_submit():
        from_cur = request.form['from_cur']
        to_cur = request.form['to_cur']

        headers = {"accept": "application/json"}
        convert_url = "{}/convert?api_key={}&from={}&to={}&amount={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], form.from_cur.data.code, form.to_cur.data.code, form.amount.data)
        response = requests.get(convert_url, headers=headers)
        
        if response.status_code == 200:
            json_obj = response.json()  
            result= json_obj['result']
            exchange_rate = result['rate']
            convert_result = result[form.to_cur.data.code]
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
    return render_template('convert.html', form=form, user=current_user, exchange_rate=exchange_rate, convert_result=convert_result, currencies=currencies, from_cur=from_cur, to_cur=to_cur)


@currency_bp.route('/historical', methods=['GET', 'POST'])
@login_required
def historical_exchange_rate():
    form = HistoricalRateChangesForm()
    currencies = Currency.query.all()
    from_cur=None
    to_cur='USD'
    results= None
    changes=None
    if current_user.default_cur != None:
        from_cur = current_user.default_cur

    if request.method == 'POST' and form.validate_on_submit():
        from_cur = request.form['from_cur']
        to_cur = request.form['to_cur']
        duration=form.duration.data

        end_date = datetime.now()
        if duration.endswith('d'):   
            start_date = end_date - timedelta(days=int(duration[:-1]))
        elif duration.endswith('m'):   
            start_date = end_date - relativedelta(months=int(duration[:-1]))
        elif duration.endswith('y'):    
            start_date = end_date - relativedelta(years=int(duration[:-1]))
        print(end_date.strftime('%Y-%m-%d'))
        print(start_date)
        
        headers = {"accept": "application/json"}
        response=None
        
        # If currency for current date is not updated, thus need to use the previous date as latest currency
        while not response or 'future' in response.text:
            time_series_url = "{}/time-series?api_key={}&from={}&to={}&start={}&end={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], form.from_cur.data.code, form.to_cur.data.code,start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            response = requests.get(time_series_url, headers=headers)
            if response.status_code == 200:
                json_obj = response.json()  
                results= json_obj['results']
                end_date = max(results[to_cur].keys())
                start_date = min(results[to_cur].keys())
                changes=(results[to_cur][end_date] - results[to_cur][start_date])/results[to_cur][start_date] * 100
                changes = round(changes, 3)            
                print(results)
            else:
                if 'future' in response.text:
                    end_date = end_date - timedelta(days=1)
                print(f"Error: {response.status_code} - {response.text}")


    return render_template('historical_exchange_rate.html', form=form, user=current_user, historical_data= results, currencies=currencies, from_cur=from_cur, to_cur=to_cur, changes=changes)
