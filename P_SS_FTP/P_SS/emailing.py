import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def buildPayload(task, state):
    payload = f"| Task | State |\n|------|-------|\n| {task} | {state} |\n"
    return payload

def sendEmail(message, subject, recipient_email, sender_email, smtp_server, smtp_port, smtp_password):
    try:
        # Create a MIMEText object to represent the email content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_email)
        msg['Subject'] = subject

        # Attach the message as plain text
        with open('log.log', 'r') as file:
            data = file.read()
        message = message.format(data)
        msg.attach(MIMEText(message, 'plain'))
        filename = "log.log"
        attachment = open("log.log", "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server,smtp_port,context=context) as server:
            server.login(sender_email,smtp_password)
            print("log in to ur email was successfull ;).")
            server.sendmail(sender_email,recipient_email,msg.as_string())
    except Exception as e:
        print(f"Error: {e}")


