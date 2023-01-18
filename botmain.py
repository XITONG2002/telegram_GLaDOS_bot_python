#! /usr/bin/python
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, \
    MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from os.path import isfile
from signin import signin, sleep
import schedule
from threading import Thread

class User():

    def __init__(self, source):
        """
        定义了单个用户的属性
        id: tg用户id
        cookie: 用户提供的cookie
        status: 是否处于活动状态，即是否有正在进行的对话
        signin_log: 上一次签到日志
        """
        # source = [id, cookie]
        self.id = source[0]
        self.cookie = source[1]
        self.status = False
        self.signin_log = ""

    def save(self) -> list:
        """
        将一个用户的信息导出。
        用户的status和signin_log属性始终存在内存中，不导出到硬盘上
        """
        # res = [id, cookie]
        return [self.id, self.cookie]

class Bot(Updater):
    def __init__(
        self,
        token = "your_tg_bot_token_here", # 修改为你自己的机器人的token
        proxy = "socks5h://127.0.0.1:7891/", # 根据需求改代理ip和端口
    ):
        """
        token: telegram机器人的token，在telegram上的bot father机器人处获取
        proxy：telegram机器人在GFW内无法连接，需要科学上网
        user_info: 所有用户的字典，以用户id为键，class User为值
        """
        self.token = token
        self.proxy = proxy
        self.user_info = {}

        # 从硬盘文件加载用户信息
        self.load()

        # 继承telegram_bot中的Updater类
        super().__init__(
            token = self.token,
            use_context = False,
            request_kwargs = {"proxy_url": self.proxy}
        )

        # 为机器人添加若干指令，如“开始”“新建”“删除”“我的”“检查”“签到”等
        self.dispatcher.add_handler(CommandHandler("start", self.command_start))
        self.dispatcher.add_handler(CommandHandler("new", self.command_new))
        self.dispatcher.add_handler(CommandHandler("del", self.command_delete))
        self.dispatcher.add_handler(CommandHandler("my", self.command_my))
        self.dispatcher.add_handler(CommandHandler("check", self.command_check))
        self.dispatcher.add_handler(CommandHandler("signin", self.command_signin))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.command_recv_text))
    
    # 从文件user_info加载用户信息的函数
    def load(self):
        if isfile(r"./user_info"):
            tmp_dict = {}
            with open(r"./user_info", mode="r", encoding="utf-8") as f:
                tmp_dict = eval(f.read())
            for id in tmp_dict:
                self.user_info[id] = User(tmp_dict[id])
        
        pop_list = []
        for user_id in self.user_info:
            if self.user_info[user_id].cookie == "":
                pop_list.append(user_id)
        for user_id in pop_list:
            self.user_info.pop(user_id)

        self.save()

    # 将用户信息保存到user_info文件的函数
    def save(self):
        tmp_dict = {}
        for id in self.user_info:
            tmp_dict[id] = self.user_info[id].save()
        with open(r"./user_info", mode="w", encoding="utf-8") as f:
                f.write(str(tmp_dict))

    # 输出日志的函数（貌似没有用过）
    def printlog(self, log):
        print(log, end="\n")
        with open(r"./log.txt", mode="a", encoding="utf-8") as f:
            f.write(log+"\n\n")

    # 以下为针对各个指令做出相应的回应
    def command_start(self, bot, update):
        print("\nCommand: start")
        print(update.message.from_user)
        update.message.reply_text(
            text = "Hello, 此bot可以帮助您自动签到GLaDOS.\n<b>What's GLaODS?\nhttps://blog.fhyq-dhy.cloud/index.php/tg_bot/7.html</b>",
            parse_mode = ParseMode.HTML
        )

    def command_signin(self, bot, update):
        print("\nCommand: signin")
        from_user = update.message.from_user
        print(from_user)
        user_id = from_user["id"]
        if user_id in self.user_info:
            update.message.reply_text(text="正在签到...")
            Thread(target=signin, args=(self.bot, user_id, self.user_info[user_id])).start()
        else:
            update.message.reply_text(text="您还没有注册账号.")

    def command_new(self, bot, update):
        print("\nCommand: new")
        from_user = update.message.from_user
        print(from_user)
        user_id = from_user["id"]
        if user_id in self.user_info:
            update.message.reply_text(text="您已经注册了一个账号，无法再次新建账号.")
            return
        self.user_info[user_id] = User([user_id, ""])
        self.user_info[user_id].status = True
        update.message.reply_text(
            text = "请回复您的cookie.\n例：SID=AAO-7r7Ib6Y50hOU7CJcx4Q16KmUux3E_TPrEITi2J3yzNqno1VM9DgkVItQjcDQN5dKGBA8ERDU1CP5h6YV-dIQeLJr..."
        )
        update.message.reply_text(
                text = "<b>如何查看自己的cookie？\nhttps://blog.fhyq-dhy.cloud/index.php/tg_bot/88.html</b>",
            parse_mode = ParseMode.HTML
        )

    def command_check(self, bot, update):
        print("\nCommand: check")
        from_user = update.message.from_user
        print(from_user)
        user_id = from_user["id"]
        if user_id in self.user_info and self.user_info[user_id].signin_log != "":
            update.message.reply_text(text=self.user_info[user_id].signin_log)
        else:
            update.message.reply_text(text="您还没有签到记录.")

    def command_delete(self, bot, update):
        print("\nCommand: del")
        from_user = update.message.from_user
        print(from_user)
        user_id = from_user["id"]
        if user_id in self.user_info:
            self.user_info.pop(user_id)
            self.save()
            update.message.reply_text(text="已删除.")
        else:
            update.message.reply_text(text="您没有账号.")

    def command_my(self, bot, update):
        print("\nCommand: my")
        from_user = update.message.from_user
        print(from_user)
        user_id = from_user["id"]
        if user_id in self.user_info and self.user_info[user_id].cookie != "":
            update.message.reply_text(text=f"您拥有一个账号.\ncookie: {self.user_info[user_id].cookie}")
        else:
            update.message.reply_text(text="您还没有注册账号.")

    # 收到字符串，判断是否有活动中的会话
    def command_recv_text(self, bot, update):
        msg = update.message
        from_user = msg.from_user
        text = msg.text
        print(f"recieve text from {from_user}, content: {text}.")
        user_id = from_user["id"]
        if not user_id in self.user_info:
            msg.reply_text("您没有活动中的会话，请输入一个命令以开始会话.")
        else:
            if not self.user_info[user_id].status:
                msg.reply_text("您没有活动中的会话，请输入一个命令以开始会话.")
            else:
                self.user_info[user_id].cookie = text
                self.user_info[user_id].status = False
                self.save()
                msg.reply_text("回复成功，正在进行第一次签到...")
                Thread(target=signin, args=(self.bot, user_id, self.user_info[user_id])).start()

    # 多线程自动签到函数
    def auto_sign_in(self):
        for user_id in self.user_info:
            Thread(target=signin, args=(self.bot, user_id, self.user_info[user_id])).start()

    def run(self):
        self.start_polling()

def run():
    tgBot = Bot()
    # 每天9:30自动签到一次
    schedule.every().day.at("09:30").do(tgBot.auto_sign_in)
    tgBot.run()
    while True:
        sleep(60)
        schedule.run_pending()

if __name__ == "__main__":
    run()
