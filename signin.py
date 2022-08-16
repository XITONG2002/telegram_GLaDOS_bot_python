#! /usr/bin/python
import requests
import json
from mail import Mail
 
def start(cookie):
  # 创建一个session,作用会自动保存cookie
  session = requests.session()
  # 点签到之后的页
  url= "https://glados.rocks/api/user/checkin"
  url2= "https://glados.rocks/api/user/status"
  referer = 'https://glados.rocks/console/checkin'
  origin = "https://glados.rocks"
  useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
  #请求负载
  payload={
      'token': 'glados.network'
  }
  # referer 当浏览器向web服务器发送请求的时候，一般会带上Referer，告诉服务器我是从哪个页面链接过来的，服务器 籍此可以获得一些信息用于处理。
  # json.dumps请求序列化
  checkin = session.post(url,headers={'cookie': cookie ,'referer': referer,'origin':origin,'user-agent':useragent,'content-type':'application/json;charset=UTF-8'},data=json.dumps(payload))
  state =  session.get(url2,headers={'cookie': cookie ,'referer': referer,'origin':origin, 'user-agent':useragent})
  if 'message' in checkin.text:
      mess = checkin.json()['message']
      time = state.json()['data']['leftDays']
      time = time.split('.')[0]
      text = mess +'，you have '+time+' days left'
      return text
 
def signin(cookie, receiver):
  signres = "success"
  try:
        text = start(cookie=cookie)
  except Exception as e:
      signres = str(e)
  mail = Mail(receiver=receiver)
  mailres = mail.send(text)
  if signres == "success" and mailres == "success":
      return ("success", text)
  elif signres == "success":
      return ("error", text, mailres)
  else:
      return ("error", signres, mailres)
