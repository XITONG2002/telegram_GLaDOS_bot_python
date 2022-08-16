#! /usr/bin/python
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, \
  MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from os.path import isfile
from signin import signin
from time import time, localtime, sleep
import schedule
 
class Bot(Updater):
  def __init__(
      self,
      token = "your_telegram_bot_token_here",
      proxy = "socks5h://127.0.0.1:7891/",
  ):
      self.token = token
      self.proxy = proxy
      self.user_dict = {}
      self.user_situation = {}
      self.user_signin_log = {}
      if isfile(r"./user_dict"):
          with open(r"./user_dict", mode="r", encoding="utf-8") as f:
              self.user_dict = eval(f.read())
      else:
          with open(r"./user_dict", mode="w", encoding="utf-8") as f:
              f.write("{}")
      if isfile(r"./signin_log"):
          with open(r"./signin_log", mode="r", encoding="utf-8") as f:
              self.user_signin_log = eval(f.read())
      else:
          with open(r"./signin_log", mode="w", encoding="utf-8") as f:
              f.write("{}")
      super().__init__(
          token = self.token,
          use_context = False,
          request_kwargs = {"proxy_url": self.proxy}
      )
      self.add_command_handler({
          "start": self.command_start,
          "new": self.command_new,
          "del": self.command_delete,
          "my": self.command_my,
          "check": self.command_check,
          "signin": self.command_signin
      })
      self.add_callback_handler(self.command_callback)
      self.add_text_handler(self.command_recv_text)
 
  def get_today(self):
      nowtime = localtime(time())
      return f"{nowtime.tm_year}.{nowtime.tm_mon}.{nowtime.tm_mday}"
 
  def add_command_handler(self, commands):
      for cmd in commands:
          self.dispatcher.add_handler(
              CommandHandler(cmd, commands[cmd])
          )
  def add_callback_handler(self, cmd):
      self.dispatcher.add_handler(CallbackQueryHandler(cmd))
  def add_text_handler(self, cmd):
      self.dispatcher.add_handler(MessageHandler(Filters.text, cmd))
 
  def command_signin(self, bot, update):
      print("\nCommand: signin")
      from_user = update.message.from_user
      print(from_user)
      from_user = from_user["id"]
      if from_user in self.user_dict:
          update.message.reply_text(text="正在签到...")
          cookie = self.user_dict[from_user]["cookie"]
          email = self.user_dict[from_user]["email"]
          res = signin(cookie, email)
          if res[0] == "success":
              self.user_signin_log[from_user]["day"] = self.get_today()
              self.user_signin_log[from_user]["res"] = res[1]
          else:
              self.user_signin_log[from_user]["day"] = self.get_today()
              self.user_signin_log[from_user]["res"] = f"部分出错.\n签到结果：{res[1]}；\n发送邮件结果：{res[2]}."
          day = self.user_signin_log[from_user]["day"]
          res = self.user_signin_log[from_user]["res"]
          update.message.reply_text(text=f"时间：{day} （UTC+8）\n结果：{res}")
          with open(r"./signin_log", mode="w", encoding="utf-8") as f:
              f.write(str(self.user_signin_log))
      else:
          update.message.reply_text(text="您还没有注册账号.")
 
  def command_start(self, bot, update):
      print("\nCommand: start")
      print(update.message.from_user)
      update.message.reply_text(
          text = "Hello, 此bot可以帮助您自动签到GLaDOS.\n<b>What's GLaODS?\nhttps://blog.fhyq-dhy.cloud/index.php/tg_bot/7.html</b>",
          parse_mode = ParseMode.HTML
      )
 
  def command_new(self, bot, update):
      print("\nCommand: new")
      from_user = update.message.from_user
      print(from_user)
      from_user = from_user["id"]
      if from_user in self.user_dict:
          update.message.reply_text(text="您已经注册了一个账号，无法再次新建账号.")
          return
      self.user_situation[from_user] = {}
      update.message.reply_text(
          text = "请依次点击下面的按钮并按提示操作：",
          reply_markup = InlineKeyboardMarkup(
              [
                  [InlineKeyboardButton(text="cookie", callback_data="cookie")],
                  [InlineKeyboardButton(text="绑定邮箱", callback_data="email")],
                  [InlineKeyboardButton(text="确定", callback_data="confirm")]
              ]
          )
      )
 
  def command_check(self, bot, update):
      print("\nCommand: check")
      from_user = update.message.from_user
      print(from_user)
      from_user = from_user["id"]
      if from_user in self.user_signin_log:
          day = self.user_signin_log[from_user]["day"]
          res = self.user_signin_log[from_user]["res"]
          update.message.reply_text(text=f"时间：{day} （UTC+8）\n结果：{res}")
      else:
          update.message.reply_text(text="您还没有签到记录.")
 
  def command_delete(self, bot, update):
      print("\nCommand: del")
      from_user = update.message.from_user
      print(from_user)
      from_user = from_user["id"]
      if from_user in self.user_dict:
          self.user_dict.pop(from_user)
          self.user_signin_log.pop(from_user)
          with open(r"./user_dict", mode="w", encoding="utf-8") as f:
              f.write(str(self.user_dict))
          with open(r"./signin_log", mode="w", encoding="utf-8") as f:
              f.write(str(self.user_signin_log))
          update.message.reply_text(text="已删除.")
      else:
          update.message.reply_text(text="您还没有注册账号.")
 
  def command_my(self, bot, update):
      print("\nCommand: my")
      from_user = update.message.from_user
      print(from_user)
      from_user = from_user["id"]
      if from_user in self.user_dict:
          email = self.user_dict[from_user]["email"]
          update.message.reply_text(text=f"email: {email}")
      else:
          update.message.reply_text(text="您还没有注册账号.")
 
  def cookie_handler(self, bot, from_user):
      bot.send_message(
          chat_id = from_user,
          text = "请按以下格式回复您的cookie：\n<b>cookie:[your cookie]</b>\n例：cookie:SID=AAO-7r7Ib6Y50hOU7CJcx4Q16KmUux3E_TPrEITi2J3yzNqno1VM9DgkVItQjcDQN5dKGBA8ERDU1CP5h6YV-dIQeLJr\n\n如何查看自己的cookie？\n    1.进入到签到页面；\n    2.按F12进入调试界面；\n    3.选择网络，刷新一次界面；\n    4.点击新出现的“checkin”选项，下拉到“请求标头”部分，即可查看到cookie.",
          parse_mode = ParseMode.HTML
      )
 
  def email_handler(self, bot, from_user):
      bot.send_message(
          chat_id = from_user,
          text = "请按以下格式回复您的邮箱：\n<b>email:[your email]</b>\n例：\nemail:qwe123@email.com",
          parse_mode = ParseMode.HTML
      )
 
  def confirm_handler(self, bot, from_user):
      if "cookie" in self.user_situation[from_user] and \
          "email" in self.user_situation[from_user]:
          if self.user_situation[from_user]["cookie"] != "" and \
              self.user_situation[from_user]["email"] != "":
              bot.send_message(
                  chat_id = from_user,
                  text = "正在验证...请稍等..."
              )
              cookie = self.user_situation[from_user]["cookie"]
              email = self.user_situation[from_user]["email"]
              res = signin(cookie, email)
              if res[0] == "success":
                  self.user_dict[from_user] = self.user_situation[from_user]
                  self.user_signin_log[from_user] = {}
                  self.user_signin_log[from_user]["day"] = self.get_today()
                  self.user_signin_log[from_user]["res"] = res[1]
                  with open(r"./signin_log", mode="w", encoding="utf-8") as f:
                      f.write(str(self.user_signin_log))
                  self.user_situation.pop(from_user)
                  with open("./user_dict", mode="w", encoding="utf-8") as f:
                      f.write(str(self.user_dict))
                  bot.send_message(
                      chat_id = from_user,
                      text = f"您已经成功注册了一个账号，已经自动为您签到一次，结果为：{res[1]}."
                  )
              else:
                  self.user_situation.pop(from_user)
                  signres, emailres = res[1], res[2]
                  bot.send_message(
                      chat_id = from_user,
                      text = f"配置错误...\n结果：签到结果：{signres}\n邮箱发送结果：{emailres}.\n请重新配置."
                  )
          else:
              bot.send_message(
                      chat_id = from_user,
                      text = "请先完成配置."
                  )
      else:
          bot.send_message(
                  chat_id = from_user,
                  text = "请先完成配置."
              )
 
  def command_callback(self, bot, update):
      data = update.callback_query.data
      from_user = update.callback_query.from_user
      if data == "cookie":
          self.cookie_handler(bot, from_user["id"])
      elif data == "email":
          self.email_handler(bot, from_user["id"])
      elif data == "confirm":
          self.confirm_handler(bot, from_user["id"])
 
  def command_recv_text(self, bot, update):
      msg = update.message
      from_user = msg.from_user["id"]
      text = msg.text
      if not from_user in self.user_situation:
          msg.reply_text("您没有活动中的会话，请输入一个命令以开始会话.")
      else:
          if text[:7] == "cookie:":
              self.user_situation[from_user]["cookie"] = text[7:]
              msg.reply_text("OK...请点击下一个按钮.")
          elif text[:6] == "email:":
              self.user_situation[from_user]["email"] = text[6:]
              msg.reply_text("OK...请点击下一个按钮.")
          else:
              msg.reply_text("输入格式错误，请重新输入.")
 
  def auto_sign_in(self):
      for user in self.user_dict:
          cookie = self.user_dict[user]["cookie"]
          email = self.user_dict[user]["email"]
          res = signin(cookie, email)
          if res[0] == "success":
              self.user_signin_log[user]["day"] = self.get_today()
              self.user_signin_log[user]["res"] = res[1]
          else:
              self.user_signin_log[user]["day"] = self.get_today()
              self.user_signin_log[user]["res"] = f"部分出错.\n签到结果：{res[1]}；\n发送邮件结果：{res[2]}."
      with open(r"./signin_log", mode="w", encoding="utf-8") as f:
          f.write(str(self.user_signin_log))
 
  def run(self):
      self.start_polling()
 
def run():
  tgBot = Bot()
  schedule.every().day.at("09:30").do(tgBot.auto_sign_in)
  tgBot.run()
  while True:
      sleep(60)
      schedule.run_pending()
 
if __name__ == "__main__":
  run()
