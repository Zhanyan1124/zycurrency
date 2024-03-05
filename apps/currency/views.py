from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from .forms import ConvertForm, HistoricalRateChangesForm, CreateExRateNotificationForm
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


@currency_bp.route('/historical', methods=['GET', 'POST'])
@login_required
def historical_exchange_rate():
    convert_form = HistoricalRateChangesForm()
    notification_form = CreateExRateNotificationForm()
    currencies = Currency.query.all()
    from_cur=None
    to_cur='USD'
    results= None
    changes=None
    if current_user.default_cur != None:
        from_cur = current_user.default_cur
    
    if request.method == 'POST' :
        for field, value in request.form.items():
            print(f"{field}: {value}")

        if convert_form.validate_on_submit():

            duration=convert_form.duration.data
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
                time_series_url = "{}/time-series?api_key={}&from={}&to={}&start={}&end={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'], convert_form.from_cur.data.code, convert_form.to_cur.data.code,start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
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

        elif notification_form.is_submitted():
            try:
                from_cur = notification_form.from_cur.data
                to_cur = notification_form.to_cur.data
                alert_type = notification_form.alert_type.data
                period = notification_form.period.data
                condition = notification_form.condition.data
                rate = notification_form.rate.data
                notify_in_app = notification_form.notify_in_app.data
                notify_email = notification_form.notify_email.data
                notes = notification_form.notes.data

                if from_cur is None:
                    notification_form.from_cur.errors.append('From currency is required')
                    raise DataMissingException('Select currency to proceed')
                if to_cur is None:
                    notification_form.to_cur.errors.append('To currency is required')
                    raise DataMissingException('Select currency to proceed')
                if not (notify_in_app or notify_email):
                    raise DataMissingException('Please check at least one notification method.')
                
                if alert_type == 'periodically':
                    rate = 0
                    condition = None

                elif alert_type == 'conditionally':
                    period = None
                    if rate is None:
                        notification_form.rate.errors = list(notification_form.rate.errors) 
                        notification_form.rate.errors.append('Exchange rate is required')
                        raise DataMissingException('Input exchange rate to proceed')
                
                new_notification = Notification(user_id = current_user.id, from_cur_code = from_cur, to_cur_code = to_cur, alert_type = alert_type, period = period, condition = condition, rate = rate, notify_in_app = notify_in_app, notify_email =  notify_email, notes = notes, is_enabled = True ) 
                db.session.add(new_notification)
                db.session.commit()
                # message = 'Notification set successfully.'
                flash('Notification set successfully.', 'success')

            except DataMissingException as e:
                print(str(e))
                flash(str(e), 'danger')
                # message = str(e) 
            except Exception as e:
                print(str(e))
                flash(f'Error when setting notification: {str(e)}', 'danger')
                # message = 'Error when setting notification: ' + str(e) 
                    

    return render_template('historical_exchange_rate.html', convert_form=convert_form, notification_form = notification_form, user=current_user, historical_data= results, currencies=currencies, from_cur=from_cur, to_cur=to_cur, changes=changes)
