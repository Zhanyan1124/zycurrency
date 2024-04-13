from apps.alert.models import Alert
from apps.notification.models import Notification
from apps.currency.utils import get_latest_rate, get_rsi_value
import requests
from apps.database import db
from datetime import datetime

def periodically_currency_update(app, duration):
    with app.app_context():
        alerts = Alert.query.filter_by(alert_type = 'periodically', is_enabled = True, period = duration)
        for alert in alerts:
            create_notification = alert.notify_in_app
            if alert.indicator == "exrate":
                response = get_latest_rate(alert.from_cur_code, alert.to_cur_code)
                if response.status_code == 200:
                    json_obj = response.json()
                    result= json_obj['result']
                    exchange_rate = result[alert.to_cur_code]
                    # print(f"Exchange rate for {alert.from_cur_code} to {alert.to_cur_code}: {exchange_rate}")
                    text = f"Today's rate for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> 1 {alert.from_cur_code} = {exchange_rate} {alert.to_cur_code} </strong>"
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    create_notification = False

            elif alert.indicator == "rsi":
                changes, date, rsi_value = get_rsi_value(alert.from_cur_code, alert.to_cur_code, '1d')
                latest_rsi = rsi_value[-1]
                if latest_rsi:
                    text = f"Today's RSI value for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> {latest_rsi} </strong>"
                    # print(f"RSI value for {alert.from_cur_code} to {alert.to_cur_code}: {latest_rsi}")
                else:
                    print(f"Error retrieving the latest rsi")
                    create_notification = False

            if create_notification:
                title = alert.period.capitalize() + " Currency Update"
                new_notification = Notification(title = title, text = text, alert_id = alert.id, user_id = alert.user_id, created_time = datetime.now())
                db.session.add(new_notification)
                db.session.commit()

def alert_condition_check(app):
    with app.app_context():
        alerts = Alert.query.filter_by(alert_type = 'conditionally', is_enabled = True)
        for alert in alerts:
            threshold_met = False
            if alert.indicator == "exrate":
                response = get_latest_rate(alert.from_cur_code, alert.to_cur_code)
                if response.status_code == 200:
                    json_obj = response.json()
                    result= json_obj['result']
                    exchange_rate = result[alert.to_cur_code]
                    # print(f"Exchange rate for {alert.from_cur_code} to {alert.to_cur_code}: {exchange_rate}")
                    if alert.condition == "more" and exchange_rate > alert.rate:
                        threshold_met = True
                        text = f"The current rate for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> 1 {alert.from_cur_code} = {exchange_rate} {alert.to_cur_code} </strong> <br> which is <strong>></strong> rate threshold <strong> {alert.rate} </strong>"
                    elif alert.condition == "less" and exchange_rate < alert.rate:
                        threshold_met = True
                        text = f"The current rate for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> 1 {alert.from_cur_code} = {exchange_rate} {alert.to_cur_code} </strong> <br> which is <strong><</strong> rate threshold <strong> {alert.rate} </strong>"


                else:
                    print(f"Error: {response.status_code} - {response.text}")

            elif alert.indicator == "rsi":
                changes, date, rsi_value = get_rsi_value(alert.from_cur_code, alert.to_cur_code, '1d')
                latest_rsi = rsi_value[-1]
                if latest_rsi:
                    # print(f"RSI value for {alert.from_cur_code} to {alert.to_cur_code}: {latest_rsi}")
                    if alert.condition == "more" and latest_rsi > alert.rsi_val:
                        threshold_met = True
                        text = f"The current RSI value for {alert.from_cur_code} to {alert.to_cur_code} is <strong> {latest_rsi} </strong> <br> which is <strong>></strong> threshold <strong>{alert.rsi_val}</strong>"

                    elif alert.condition == "less" and latest_rsi < alert.rsi_val:
                        threshold_met = True
                        text = f"The current RSI value for {alert.from_cur_code} to {alert.to_cur_code} is <strong> {latest_rsi} </strong> <br> which is <strong><</strong> threshold <strong>{alert.rsi_val}</strong>"

                else:
                    print(f"Error retrieving the latest rsi")

            if threshold_met:
                alert.is_enabled=False
                if alert.notify_in_app:
                    title = "Alert Threshold has been Met"
                    new_notification = Notification(title = title, text = text, alert_id = alert.id, user_id = alert.user_id, created_time = datetime.now())
                    db.session.add(new_notification)
                db.session.commit()
