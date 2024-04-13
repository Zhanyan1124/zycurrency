from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from .forms import ConvertForm
from flask_wtf.csrf import generate_csrf
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .utils import get_latest_rate, get_rsi_value
import requests
from apps.models import Currency
from apps.alert.models import Alert
from .exceptions import DataMissingException
from apps.database import db
import json

currency_bp = Blueprint('currency', __name__, template_folder='templates')

@currency_bp.route('/convert', methods=['GET'])
@login_required
def convert():
    from_cur=current_user.default_cur
    to_cur=current_user.second_cur
    currencies = Currency.query.all()
        
    return render_template('convert.html', user=current_user, currencies=currencies, from_cur=from_cur, to_cur=to_cur, csrf_token = generate_csrf())

@currency_bp.route('/historical-exrate', methods=['GET'])
@login_required
def historical_exchange_rate():
    currencies = Currency.query.all()
    from_cur= current_user.default_cur
    to_cur=current_user.second_cur
    
    return render_template('historical_exchange_rate.html', csrf_exrate_token = generate_csrf(), csrf_alert_token = generate_csrf(), currencies=currencies, from_cur=from_cur, to_cur=to_cur)

@currency_bp.route('/historical-rsi', methods=['GET'])
@login_required
def historical_rsi_value():
    currencies = Currency.query.all()
    from_cur = current_user.default_cur
    to_cur=current_user.second_cur

    return render_template('historical_rsi_value.html', csrf_rsi_token = generate_csrf(), csrf_alert_token = generate_csrf(), currencies=currencies, from_cur=from_cur, to_cur=to_cur)

@currency_bp.route('/comparison', methods=['GET'])
@login_required
def currency_comparison():
    currencies = Currency.query.all()
    base_cur = current_user.default_cur
    popular_curs = current_app.config["POPULAR_CURRENCIES"]

    fav_curs = None
    if current_user.fav_curs:
        fav_curs = current_user.fav_curs.split(',')
        if base_cur in fav_curs:
            fav_curs.remove(base_cur)

    if base_cur in popular_curs:
        popular_curs.remove(base_cur)


    
    return render_template('currency_comparison.html', csrf_token = generate_csrf(), currencies=currencies, base_cur=base_cur, popular_curs=popular_curs, fav_curs=fav_curs)

@currency_bp.route('/correlation-analysis', methods=['GET'])
@login_required
def currency_correlation_analysis():
    currencies = Currency.query.all()
    popular_curs = current_app.config["POPULAR_CURRENCIES"]
    fav_curs = None
    if current_user.fav_curs:
        fav_curs = current_user.fav_curs.split(',')
    
    return render_template('currency_correlation.html', csrf_token = generate_csrf(), currencies=currencies, popular_curs=popular_curs, fav_curs=fav_curs)

@currency_bp.route('/latest-exrate', methods=['POST'])
def retrieve_latest_rate():
    try:
        from_cur = request.form.get('from_cur')
        to_cur = request.form.get('to_cur')

        if from_cur is None or to_cur is None:
            raise DataMissingException('Select currency to proceed')

        response = get_latest_rate(from_cur, to_cur)
        if response.status_code == 200:
            json_obj = response.json()
            print(json_obj)  
            result= json_obj['result']
            exchange_rate = result[to_cur]
            updated = json_obj['updated']
            updated_date, updated_time = updated.split(" ")
            data = {
                "updated_date": updated_date,
                "updated_time": updated_time,
                "exchange_rate": exchange_rate,
            }
            return jsonify(data), 200
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return jsonify({'error': str(e)}), 400
    
    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

@currency_bp.route('/convert', methods=['POST'])
@login_required
def retrieve_convertion():
    try:
        from_cur = request.form.get('from_cur')
        to_cur = request.form.get('to_cur')
        amount=request.form.get('amount')

        if from_cur is None or to_cur is None:
            raise DataMissingException('Select currency to proceed')
        
        elif amount is None:
            raise DataMissingException('Please input amount')

        headers = {"accept": "application/json"}
        convert_url = "{}/convert?api_key={}&from={}&to={}&amount={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], from_cur, to_cur, amount)
        response = requests.get(convert_url, headers=headers)

        if response.status_code == 200:
            json_obj = response.json()
            print(json_obj)  
            result= json_obj['result']
            exchange_rate = result['rate']
            convert_result = result[to_cur]
            data = {
                "convert_result": convert_result,
                "exchange_rate": exchange_rate,
            }
            return jsonify(data), 200
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return jsonify({'error': str(e)}), 400
    
    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

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

        if from_cur is None or to_cur is None:
            raise DataMissingException('Select currency to proceed')
        if duration is None:
            raise DataMissingException('Select duration to proceed')

        changes, dates, rsi_values = get_rsi_value(from_cur, to_cur, duration)
        data = {
            "dates": dates,
            "rsi_values": rsi_values,
            "changes" : changes
        }
        return jsonify(data), 200
    
    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

@currency_bp.route('/comparison', methods=['POST'])
@login_required
def retrieve_currency_comparison():
    try:
        request_json = request.get_json()
        print(request_json)

        base_cur = request_json.get('base_cur')
        compare_curs = request_json.get('compare_curs')
        duration = request_json.get('duration')

        if base_cur is None or compare_curs is None:
            raise DataMissingException('Select currency to proceed')
        if duration is None:
            raise DataMissingException('Select duration to proceed')

        end_date = datetime.now()
        if duration.endswith('d'):   
            start_date = end_date - timedelta(days=int(duration[:-1]))
        elif duration.endswith('m'):   
            start_date = end_date - relativedelta(months=int(duration[:-1]))
        elif duration.endswith('y'):    
            start_date = end_date - relativedelta(years=int(duration[:-1]))

        headers = {"accept": "application/json"}
        response=None
        compare_curs_csv= ','.join(compare_curs)
        while not response or 'future' in response.text:
            fetch_exrate_url = "{}/fetch-multi?api_key={}&from={}&to={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], base_cur, compare_curs_csv)
            response = requests.get(fetch_exrate_url, headers=headers)
            up_to_date = False
            while not up_to_date:
                if response.status_code == 200:
                    json_obj = response.json()  
                    current_results= json_obj['results']
                    updated_date = json_obj['updated']
                    # Check if today data has been updated, if not updated then the api will return the same data (yesterday) for both historical and current exchange rate 
                    # if user chose 1 day duration
                    if updated_date[:10] != str(start_date)[:10]:
                        up_to_date = True
                    else:
                        start_date = start_date - timedelta(days=int(duration[:-1]))

                elif 'future' in response.text:
                    end_date = end_date - timedelta(days=1)
                    print(f"Error: {response.status_code} - {response.text}")

                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    return jsonify({'error': str(e)}), 400
                
            fetch_historical_exrate_url = "{}/historical?api_key={}&date={}&from={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], start_date.strftime('%Y-%m-%d'), base_cur)
            response = requests.get(fetch_historical_exrate_url, headers=headers)
            if response.status_code == 200:
                json_obj = response.json()  
                historical_results= json_obj['results']
            
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return jsonify({'error': str(e)}), 400

            data = []
            for currency in compare_curs:
                current_rate = current_results[currency]
                historical_rate = historical_results[currency]
                changes = (current_rate- historical_rate)/historical_rate * 100
                data.append({'currency': currency, 'exchange_rate': current_rate, 'historical_rate': historical_rate, 'changes': changes })            
            return jsonify(data), 200
    
    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400


@currency_bp.route('/correlation-analysis', methods=['POST'])
@login_required
def retrieve_currency_correlation():
    try:
        request_json = request.get_json()
        print(request_json)

        input_curs = request_json.get('input_curs')
        duration = request_json.get('duration')
        print(input_curs)
        print(duration)

        if len(input_curs) <2:
            raise DataMissingException('Select currency to proceed')
        if duration is None:
            raise DataMissingException('Select duration to proceed')

        end_date = datetime.now()
        if duration.endswith('d'):   
            start_date = end_date - timedelta(days=int(duration[:-1]))
        elif duration.endswith('m'):   
            start_date = end_date - relativedelta(months=int(duration[:-1]))
        elif duration.endswith('y'):    
            start_date = end_date - relativedelta(years=int(duration[:-1]))

        headers = {"accept": "application/json"}

        curs_csv= ','.join(input_curs)
        results = []
        for base_cur in input_curs:
            data=[]
            response=None
            while not response or 'future' in response.text:
                fetch_exrate_url = "{}/fetch-multi?api_key={}&from={}&to={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], base_cur, input_curs)
                response = requests.get(fetch_exrate_url, headers=headers)
                up_to_date = False
                while not up_to_date:
                    if response.status_code == 200:
                        json_obj = response.json()  
                        current_results= json_obj['results']
                        updated_date = json_obj['updated']
                        # Check if today data has been updated, if not updated then the api will return the same data (yesterday) for both historical and current exchange rate 
                        # if user chose 1 day duration
                        if updated_date[:10] != str(start_date)[:10]:
                            up_to_date = True
                        else:
                            start_date = start_date - timedelta(days=int(duration[:-1]))

                    elif 'future' in response.text:
                        end_date = end_date - timedelta(days=1)
                        print(f"Error: {response.status_code} - {response.text}")
                    else:
                        print(f"Error: {response.status_code} - {response.text}")
                        return jsonify({'error': str(e)}), 400
                    
                fetch_historical_exrate_url = "{}/historical?api_key={}&date={}&from={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], start_date.strftime('%Y-%m-%d'), base_cur)
                response = requests.get(fetch_historical_exrate_url, headers=headers)
                if response.status_code == 200:
                    json_obj = response.json()  
                    historical_results= json_obj['results']
                
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    return jsonify({'error': str(e)}), 400

                for currency in input_curs:
                    current_rate = current_results[currency]
                    historical_rate = historical_results[currency]
                    changes = (current_rate- historical_rate)/historical_rate * 100
                    data.append({'x': currency, 'y': f'{changes:.3f}%'})
                print(json.dumps(data))
                results.append({'name': base_cur, 'data':data})

        print(json.dumps(results))        
        return jsonify(results), 200
    
    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400
