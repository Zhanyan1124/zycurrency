from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from .forms import ConvertForm
from flask_wtf.csrf import generate_csrf
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
from apps.models import Currency
from apps.notification.models import Notification
from .exceptions import DataMissingException
from apps import db

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


@currency_bp.route('/historical-exrate', methods=['GET'])
@login_required
def historical_exchange_rate():
    currencies = Currency.query.all()
    from_cur=None
    to_cur='USD'

    if current_user.default_cur is not None:
        from_cur = current_user.default_cur
    
    return render_template('historical_exchange_rate.html', csrf_exrate_token = generate_csrf(), csrf_notification_token = generate_csrf(), currencies=currencies, from_cur=from_cur, to_cur=to_cur)

@currency_bp.route('/historical-rsi', methods=['GET'])
@login_required
def historical_rsi_value():
    currencies = Currency.query.all()
    from_cur=None
    to_cur='USD'

    if current_user.default_cur is not None:
        from_cur = current_user.default_cur
    
    return render_template('historical_rsi_value.html', csrf_rsi_token = generate_csrf(), csrf_notification_token = generate_csrf(), currencies=currencies, from_cur=from_cur, to_cur=to_cur)


@currency_bp.route('/historical-exrate', methods=['POST'])
@login_required
def retrieve_historical_exchange_rate():
    try:
        from_cur = request.form.get('from_cur')
        to_cur = request.form.get('to_cur')
        duration=request.form.get('duration')
        end_date = datetime.now()
        if from_cur is None or to_cur is None:
            raise DataMissingException('Select currency to proceed')
        if duration is None:
            raise DataMissingException('Select duration to proceed')

        if duration.endswith('d'):   
            start_date = end_date - timedelta(days=int(duration[:-1]))
        elif duration.endswith('m'):   
            start_date = end_date - relativedelta(months=int(duration[:-1]))
        elif duration.endswith('y'):    
            start_date = end_date - relativedelta(years=int(duration[:-1]))
    
        headers = {"accept": "application/json"}
        response=None
    
        # If currency for current date is not updated, thus need to use the previous date as latest currency
        while not response or 'future' in response.text:
            time_series_url = "{}/time-series?api_key={}&from={}&to={}&start={}&end={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], from_cur, to_cur, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            response = requests.get(time_series_url, headers=headers)
            if response.status_code == 200:
                json_obj = response.json()  
                results= json_obj['results']
                end_date = max(results[to_cur].keys())
                start_date = min(results[to_cur].keys())
                changes=(results[to_cur][end_date] - results[to_cur][start_date])/results[to_cur][start_date] * 100
                changes = round(changes, 4)
                data = {
                    "results": results,
                    "changes": changes
                }
                return jsonify(data), 200
            else:
                if 'future' in response.text:
                    end_date = end_date - timedelta(days=1)
                print(f"Error: {response.status_code} - {response.text}")
    
    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400


@currency_bp.route('/historical-rsi', methods=['POST'])
@login_required
def retrieve_historical_rsi_values():
    try:
        from_cur = request.form.get('from_cur')
        to_cur = request.form.get('to_cur')
        duration=request.form.get('duration')
        end_date = datetime.now()
        if from_cur is None or to_cur is None:
            raise DataMissingException('Select currency to proceed')
        if duration is None:
            raise DataMissingException('Select duration to proceed')

        if duration.endswith('d'):   
            start_date = end_date - timedelta(days=int(duration[:-1]))
        elif duration.endswith('m'):   
            start_date = end_date - relativedelta(months=int(duration[:-1]))
        elif duration.endswith('y'):    
            start_date = end_date - relativedelta(years=int(duration[:-1]))
        start_date = start_date - timedelta(days=14)
        print(end_date)
        print(start_date)
        headers = {"accept": "application/json"}
        response=None
    
        # If currency for current date is not updated, thus need to use the previous date as latest currency
        while not response or 'future' in response.text:
            time_series_url = "{}/time-series?api_key={}&from={}&to={}&start={}&end={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], from_cur, to_cur, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            response = requests.get(time_series_url, headers=headers)
            if response.status_code == 200:
                json_obj = response.json()  
                results= json_obj['results']
                dates =  list(list(results.values())[0].keys())
                exchange_rates = list(list(results.values())[0].values())

                print("Dates:", list(dates))
                print("Exchange Rates:", list(exchange_rates))

                changes = []
                for i in range(1, len(exchange_rates)):
                    if exchange_rates[i] - exchange_rates[i - 1] != 0:
                        change = (exchange_rates[i] - exchange_rates[i - 1])/exchange_rates[i-1] * 100
                    else:
                        change = 0
                    changes.append(change)
                print("Changes:", list(changes))
                rsi_values = []
                for i in range(14, len(changes)+1):
                    gain = 0
                    loss = 0
                    for j in range(i-14, i):
                        if  changes[j] > 0:
                            gain += changes[j]
                        else:
                            loss -= changes[j]
                    average_gain = gain / 14
                    average_loss = loss / 14
                    relative_strength = average_gain/average_loss
                    rsi = 100-(100/(1+relative_strength))
                    print('Avg gain for '+ str(i) + ': ' + str(average_gain))
                    print('Avg loss for '+ str(i) + ': ' + str(average_loss))
                    print('RS for '+ str(i)  + ': ' + str(relative_strength))
                    print('RSI for '+ str(i)  + ': ' + str(rsi))
                    rsi_values.append(rsi)
                changes = round(rsi_values[-1] - rsi_values[0] / rsi_values[0] * 100,4)
                dates = dates[14:]
                rounded_rsi_values = [round(rsi, 1) for rsi in rsi_values]
                print("Dates:", list(dates))
                print("RSI Values:", list(rsi_values))

                data = {
                    "dates": dates,
                    "rsi_values": rsi_values,
                    "changes" : changes
                }
                return jsonify(data), 200
            else:
                if 'future' in response.text:
                    end_date = end_date - timedelta(days=1)
                print(f"Error: {response.status_code} - {response.text}")
    
    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400