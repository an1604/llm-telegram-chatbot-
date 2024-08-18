import os
from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv

load_dotenv()


def send_email(email_receiver, display_name,email_subject,email_body, from_email=None):
    email_sender = os.getenv('MAIL_USERNAME')
    email_password = os.getenv('MAIL_PASSWORD')

    em = EmailMessage()
    if from_email:
        em['from'] = f"{display_name} <{from_email}>"
    else:
        em['from'] = f"{display_name} <{email_sender}>"

    em['to'] = email_receiver
    em['subject'] = email_subject
    em.set_content(email_body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(os.getenv('MAIL_SERVER'), 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

