from celery import Celery, shared_task
from flask_mail import Message
from apps import mail 
from flask import current_app

@shared_task()
def send_periodic_notification_mail(email, period, html_template):
    print('Sending notification email')
    msg = Message(period.capitalize() + " Currency Update from ZyCurrency", 
    sender=current_app.config["MAIL_USERNAME"], 
    recipients=[email])
    msg.html = html_template
    mail.send(msg)
    return 'Sent Periodic Notification Email'

@shared_task()
def send_conditional_notification_mail(email, html_template):
    print('Sending notification email')
    msg = Message("Alert Threshold has been Met"), 
    sender=current_app.config["MAIL_USERNAME"], 
    recipients=[email]
    msg.html = html_template
    mail.send(msg)
    return 'Sent Conditional Notification Email'