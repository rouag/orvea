# -*- coding: utf-8 -*-

__author__ = 'maddouri'

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_email(recievers,sender="940@um.gov.sa",**kwargs):
    """
    :param sender: str
    :param recievers: list
    :param kwargs:
    :return:
    """

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "تأخر في المعاملة رقم %s" % kwargs['transaction number']
    msg['From'] = sender
    msg['To'] = recievers

    # Create the body of the message (a plain-text and an HTML version).
    html = """\
    <html>
      <head></head>
      <body dir="rtl" >
        <p> مرحبا بك  ,
</p><p>
نعلمكم أن
<a href="%s" >
المعاملة
</a>
 رقم %d  قد تأخرت لدى الموظف %s .
</p><p>
هذا والله الموفق,,,
        </p>
      </body>
    </html>
    """ % (kwargs["link"],kwargs['transaction number'],kwargs['employee'])

    # Record the MIME types of both parts - text/plain and text/html.
    body = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(body)

    # Send the message via local SMTP server.
    server = smtplib.SMTP('post.um.gov.sa', 587)
    server.starttls()
    server.login("940@um.gov.sa", "940@123")

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(sender, recievers, msg.as_string())
    server.quit()

# send_email('h.ibnzbiba@um.gov.sa',employee="عبد الله",link="www.google.com" ,**{'transaction number':398796})