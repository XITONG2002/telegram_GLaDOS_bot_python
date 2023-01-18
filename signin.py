#! /usr/bin/python
import requests
import json
from time import time, localtime, sleep
 
def get_today():
  nowtime = localtime(time())
  return f"{nowtime.tm_year}.{nowtime.tm_mon}.{nowtime.tm_mday}"
 
def start(cookie):
  proxies = {
          "http": "socks5://127.0.0.1:7891",
          "https": "socks5://127.0.0.1:7891"
          }
  # 创建一个session,作用会自动保存cookie
  session = requests.session()
  #点签到之后的页
  url= "https://glados.rocks/api/user/checkin"
  url2= "https://glados.rocks/api/user/status"
  referer = 'https://glados.rocks/console/checkin'
  #checkin = requests.post(url,headers={'cookie': cookie ,'referer': referer })
  #state =  requests.get(url2,headers={'cookie': cookie ,'referer': referer})
  origin = "https://glados.rocks"
  useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
  #请求负载
  payload={
      # 'token': 'glados_network'
      'token': 'glados.network'
  }
  #referer 当浏览器向web服务器发送请求的时候，一般会带上Referer，告诉服务器我是从哪个页面链接过来的，服务器 籍此可以获得一些信息用于处理。
  #json.dumps请求序列化
  checkin = session.post(url,headers={'cookie': cookie ,'referer': referer,'origin':origin,'user-agent':useragent,'content-type':'application/json;charset=UTF-8'},data=json.dumps(payload), proxies=proxies)
  state =  session.get(url2,headers={'cookie': cookie ,'referer': referer,'origin':origin,'user-agent':useragent}, proxies=proxies)
 # print(res)
  # print(checkin.text )
  if 'message' in checkin.text:
      mess = checkin.json()['message']
      time = state.json()['data']['leftDays']
      time = time.split('.')[0]
      # print(time)
      text = mess +'，you have '+time+' days left'
      #print(text)
      return text
# 签到后调用tg_bot回复结果
def signin(bot, user_id, user):
  success = True
  day = get_today()
  try:
      res = start(user.cookie)
  except Exception as e:
      success = False
      res = str(e)
  if success:
      res = f"时间：{day} （UTC+8）\n结果：{res}"
  else:
      res =  f"时间：{day} （UTC+8）\n结果：签到失败。\n原因：{res}"
  bot.send_message(
      chat_id = user_id,
      text = res
  )
  user.signin_log = res
  return
