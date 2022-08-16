#! /usr/bin/python
import smtplib
from email.mime.text import MIMEText
 
class Mail():
  def __init__(
      self,
      host = "smtp.your_host.com",
      user = "yourself@you.com",
      passwd = "your_password_here",
      sender = "yourself@you.com",
      receiver = "whomever@who.com",
  ):
      self.host = host
      self.user = user
      self.passwd = passwd
      self.sender = sender
      self.receiver = receiver
 
  def send(self, content):
      try:
          msg = MIMEText(content, "plain", "utf-8")
          msg["Subject"] = "GLaDOS Auto Sign in"
          msg["From"] = self.sender
          msg["To"] = self.receiver
          smtp = smtplib.SMTP()
          smtp.connect(self.host, 25)
          smtp.login(self.user, self.passwd)
          smtp.sendmail(self.sender, self.receiver, msg.as_string())
          smtp.quit()
         # print('Send successfully.')
      except smtplib.SMTPException as e:
         # print('error:',e) #打印错误
          return str(e)
      return "success"
 
if __name__ == "__main__":
  test = Mail()
  test.send("test")
