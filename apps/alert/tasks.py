from apps.alert.models import Alert
from apps.notification.models import Notification
from apps.auth.models import User
from apps.currency.utils import get_latest_rate, get_rsi_value
from apps.notification.tasks import send_periodic_notification_mail, send_conditional_notification_mail
import requests
from apps import db
from datetime import datetime
from flask import url_for, render_template, current_app

def periodically_currency_update(app, duration):
    with app.app_context():
        alerts = Alert.query.filter_by(alert_type = 'periodically', is_enabled = True, period = duration)
        for alert in alerts:
            create_notification = alert.notify_in_app
            send_email = alert.notify_email
            exchange_rate = None
            latest_rsi = None
            if alert.indicator == "exrate":
                response = get_latest_rate(alert.from_cur_code, alert.to_cur_code)
                if response.status_code == 200:
                    json_obj = response.json()
                    result= json_obj['result']
                    exchange_rate = result[alert.to_cur_code]
                    # print(f"Exchange rate for {alert.from_cur_code} to {alert.to_cur_code}: {exchange_rate}")
                    text = f"Today's rate for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> 1 {alert.from_cur_code} = {exchange_rate} {alert.to_cur_code} </strong>"
                    if alert.notes:
                        text += f"<br>Notes: {alert.notes}"
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    create_notification = False
                    send_email = False

            elif alert.indicator == "rsi":
                changes, date, rsi_value = get_rsi_value(alert.from_cur_code, alert.to_cur_code, '1d')
                latest_rsi = rsi_value[-1]
                if latest_rsi:
                    text = f"Today's RSI value for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> {latest_rsi} </strong>"
                    if alert.notes:
                        text += f"<br>Notes: {alert.notes}"
                    # print(f"RSI value for {alert.from_cur_code} to {alert.to_cur_code}: {latest_rsi}")
                else:
                    print(f"Error retrieving the latest rsi")
                    create_notification = False
                    send_email = False

            if create_notification:
                title = alert.period.capitalize() + " Currency Update"
                new_notification = Notification(title = title, text = text, alert_id = alert.id, user_id = alert.user_id, created_time = datetime.now())
                db.session.add(new_notification)
                db.session.commit()
            
            if send_email:
                sign_in_url = current_app.config['URL_DOMAIN_WITH_PROTOCOL'] + "/auth/login"
                print(sign_in_url)
                html_template = render_template('mails/periodic_notification_mail.html', indicator = alert.indicator, from_cur = alert.from_cur_code, to_cur = alert.to_cur_code, exchange_rate = exchange_rate, latest_rsi = latest_rsi, sign_in_url = sign_in_url, notes = alert.notes)
                user = User.query.get(alert.user_id)
                send_periodic_notification_mail.delay(user.email, alert.period, html_template)
                

def alert_condition_check(app):
    with app.app_context():
        alerts = Alert.query.filter_by(alert_type = 'conditionally', is_enabled = True)
        for alert in alerts:
            threshold_met = False
            threshold_value = None
            exchange_rate = None
            latest_rsi = None
            if alert.indicator == "exrate":
                threshold_value = alert.rate
                response = get_latest_rate(alert.from_cur_code, alert.to_cur_code)
                if response.status_code == 200:
                    json_obj = response.json()
                    result= json_obj['result']
                    exchange_rate = result[alert.to_cur_code]
                    print(f"Exchange rate for {alert.from_cur_code} to {alert.to_cur_code}: {exchange_rate}")
                    if alert.condition == "more" and exchange_rate > threshold_value:
                        threshold_met = True
                        text = f"The current rate for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> 1 {alert.from_cur_code} = {exchange_rate} {alert.to_cur_code} </strong> <br> which is <strong>></strong> rate threshold <strong> {threshold_value} </strong>"
                        if alert.notes:
                            text += f"<br>Notes: {alert.notes}"
                    elif alert.condition == "less" and exchange_rate < threshold_value:
                        threshold_met = True
                        text = f"The current rate for {alert.from_cur_code} to {alert.to_cur_code} <br> <strong> 1 {alert.from_cur_code} = {exchange_rate} {alert.to_cur_code} </strong> <br> which is <strong><</strong> rate threshold <strong> {threshold_value} </strong>"
                        if alert.notes:
                            text += f"<br>Notes: {alert.notes}"
                else:
                    print(f"Error: {response.status_code} - {response.text}")

            elif alert.indicator == "rsi":
                threshold_value = alert.rsi_val
                changes, date, rsi_value = get_rsi_value(alert.from_cur_code, alert.to_cur_code, '1d')
                latest_rsi = rsi_value[-1]
                if latest_rsi:
                    print(f"RSI value for {alert.from_cur_code} to {alert.to_cur_code}: {latest_rsi}")
                    if alert.condition == "more" and latest_rsi > threshold_value:

                        threshold_met = True
                        text = f"The current RSI value for {alert.from_cur_code} to {alert.to_cur_code} is <strong> {latest_rsi} </strong> <br> which is <strong>></strong> threshold <strong>{threshold_value}</strong>"
                        if alert.notes:
                            text += f"<br>Notes: {alert.notes}"

                    elif alert.condition == "less" and latest_rsi < threshold_value:
                        threshold_met = True
                        text = f"The current RSI value for {alert.from_cur_code} to {alert.to_cur_code} is <strong> {latest_rsi} </strong> <br> which is <strong><</strong> threshold <strong>{threshold_value}</strong>"
                        if alert.notes:
                            text += f"<br>Notes: {alert.notes}"
    
                else:
                    print(f"Error retrieving the latest rsi")

            if threshold_met:
                alert.is_enabled=False
                if alert.notify_in_app:
                    title = "Alert Threshold has been Met"
                    new_notification = Notification(title = title, text = text, alert_id = alert.id, user_id = alert.user_id, created_time = datetime.now())
                    db.session.add(new_notification)
                if alert.notify_email:
                    sign_in_url = current_app.config['URL_DOMAIN_WITH_PROTOCOL'] + "/auth/login"
                    html_template = render_template('mails/conditional_notification_mail.html', indicator = alert.indicator, from_cur = alert.from_cur_code, to_cur = alert.to_cur_code, exchange_rate = exchange_rate, latest_rsi = latest_rsi, condition = alert.condition, threshold_value = threshold_value, sign_in_url = sign_in_url, notes = alert.notes)
                    user = User.query.get(alert.user_id)
                    send_conditional_notification_mail.delay(user.email, html_template)

                db.session.commit()
