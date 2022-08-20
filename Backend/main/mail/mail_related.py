from .. import mail_sender
from flask import render_template, current_app
from flask_mail import Message
from smtplib import SMTPException


def send_mail(to, subject, template, **kwargs):
    msg = Message(subject, sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=to)
    try:
        msg.body = render_template(template + '.txt', **kwargs)
        response = mail_sender.send(msg) # envio el mensaje
    except SMTPException as e:
        print(e)
        return 'Mail Delivery Failed'
    return True

