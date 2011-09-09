#!/usr/bin/python

#imports
import sys
sys.path.append('/lib')

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def SendHTMLmail(recipient, sender, subject, message):
   """ Send an HTML email with an embedded image and a plain text message for email clients that don't want to display the HTML. """
   # Create the root message and fill in the from, to, and subject headers
   email = MIMEMultipart('related')
   email['Subject'] = subject
   email['From'] = sender
   email['To'] = recipient
   email.preamble = 'This is a multi-part message in MIME format.'

   # start the message
   alternative = MIMEMultipart('alternative')
   alternative.attach(MIMEText(message))
   email.attach(alternative)

   # Send the email (this example assumes SMTP authentication is required)
   smtp = smtplib.SMTP('mail.chrism.biz', 26)
   smtp.login("postmaster@chrism.biz", "postmaster")
   smtp.sendmail(sender, recipient, email.as_string())
   smtp.quit()
