import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import Flask, request, redirect, url_for, flash
import socket

hostname = socket.gethostname()
app = Flask(__name__)

def send_secure_email(to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password, subject, message_body):
    # Create a secure SMTP connection
    try:
        server = smtplib.SMTP_SSL(host=smtp_server, port=smtp_port)
        server.login(smtp_user, smtp_password)       
    except Exception as e:
        print("Failed to establish a secure SMTP connection:", str(e))
        return False
    # Compose the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    # Attach the message body
    msg.attach(MIMEText(message_body, 'plain'))
    # Send the email
    try:
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print("Failed to send email:", str(e))
        return False