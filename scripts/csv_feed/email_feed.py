import smtplib, ssl
from os import environ, listdir

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import date

# By default, looks for a relative 'csv' directory
def send_feed_email(csv_dir = "csv"):
  sender = environ.get("FEED_EMAIL")
  receiver = environ.get("FEED_TO")
  body = f"This is an automated email. Please see the attached competitor pricing CSVs, generated today ({date.today()})"

  message = MIMEMultipart()
  message["From"] = sender
  message["To"] = receiver
  message["Subject"] = f"Weekly Competitor Pricing Feed ({date.today()})"

  message.attach(MIMEText(body, "plain"))

  for filename in listdir(csv_dir):
    if filename.endswith(".csv"):
      with open(f"{csv_dir}/{filename}", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        
        message.attach(part)

  text = message.as_string()

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(environ.get("FEED_SMTP_SERVER"), 465, context=context) as server:
    server.login(sender, environ.get("FEED_PASS"))
    server.sendmail(sender, receiver.split(","), text)

if __name__ == '__main__':
  from dotenv import load_dotenv
  load_dotenv()

  send_feed_email()