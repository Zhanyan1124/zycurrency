from celery import Celery, shared_task
from flask_mail import Message
from apps import mail 
from flask import current_app

@shared_task()
def send_reset_password_mail(email, html_template):
    print('Executing Task')
    msg = Message("Reset your Password on ZyCurrency", 
    sender=current_app.config["MAIL_USERNAME"], 
    recipients=[email])
    msg.html = html_template
    mail.send(msg)
    return 'Sent Reset Password Email'

