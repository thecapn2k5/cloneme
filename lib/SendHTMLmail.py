import sys,os,cgi
sys.path.append('/lib')
from cgi import escape
import ConfigParser
import uuid
import re

def SendHTMLmail(to_email, email_subject, text_msg, html_msg, from_email, sendmail):
   """ Send an HTML email with an embedded image and a plain text message for
       email clients that don't want to display the HTML. """

   # Neat but a little scary
   from email.MIMEMultipart import MIMEMultipart
   from email.MIMEText import MIMEText
   from email.MIMEImage import MIMEImage

   # Create the root message and fill in the from, to, and subject headers
   msgRoot = MIMEMultipart('related')
   msgRoot['Subject'] = email_subject
   msgRoot['From'] = from_email
   msgRoot['To'] = ','.join(to_email)
   msgRoot.preamble = 'This is a multi-part message in MIME format.'

   # Encapsulate the plain and HTML versions of the message body in an
   # 'alternative' part, so message agents can decide which they want to display.
   msgAlternative = MIMEMultipart('alternative')
   msgRoot.attach(msgAlternative)

   #msgText = MIMEText('This is the alternative plain text message.')
   msgText = MIMEText(text_msg)
   msgAlternative.attach(msgText)

   # We reference the image in the IMG SRC attribute by the ID we give it below
   msgText = MIMEText(html_msg, 'html')
   msgAlternative.attach(msgText)

   # Send the email (this example assumes SMTP authentication is required)
   import smtplib
   smtp = smtplib.SMTP('mail.earningsrun.com', 25)
   smtp.login("kenny.pyatt@earningsrun.com", "qwerty99")
   #smtp.set_debuglevel(1)
   smtp.sendmail(from_email, to_email, msgRoot.as_string())
   smtp.quit()
