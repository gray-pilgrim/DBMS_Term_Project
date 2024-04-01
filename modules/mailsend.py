import smtplib
from email.mime.text import MIMEText
from random import randint

def send_email(subject, body, sender, recipients, passwordmail):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, passwordmail)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

def OTP_send(email, otp = 100000, random=False):
    if(random == True):
        otp = randint(100001, 999998)
    subject = "OTP VERIFICATION"
    body = f"Welcome to ADRRSo Database Management System\nYour OTP : {otp}"
    sender = "swlabbas0@gmail.com"
    recipients = [email, sender]
    passwordmail = "rlhxkaibxajymacx"
    send_email(subject, body, sender, recipients, passwordmail)
    return otp
    