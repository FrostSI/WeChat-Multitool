import time
from datetime import datetime
import uiautomation
from openai import OpenAI
import random
import threading
import schedule

wx = uiautomation.WindowControl(ClassName='WeChatMainWndForPC')
session = wx.ListControl(Name='会话')
client = OpenAI(api_key = open('./API_KEY.txt').readline(), base_url="https://api.moonshot.cn/v1")
log_file = open('./log.txt', 'a', encoding='utf-8')
me = ''
admin = []

def send_message_with_typing(text, min_char_delay=0.05, max_char_delay=0.2):
    """模拟人工打字发送消息"""
    for char in text:
        wx.SendKeys(text=char, waitTime=0)
        time.sleep(random.uniform(min_char_delay, max_char_delay))

def Reply_ChatGPT(message_window, sender, question_message):
    success = False
    time.sleep(random.uniform(1, 2))  # 增加延迟
    wx.SwitchToThisWindow()
    time.sleep(random.uniform(1, 2))  # 增加延迟
    message_window.Click(simulateMove=False)
    time.sleep(random.uniform(0.5, 1))
    send_message_with_typing('让我想想')
    time.sleep(random.uniform(0.5, 1))
    wx.SendKeys('{Enter}', waitTime=0)
    for tries in range(3):
        try:
            answer_message = client.chat.completions.create(model="moonshot-v1-8k", messages=[{"role": "user", "content": question_message}]).choices[0].message.content
        except:
            Log(sender + ' ' + str(tries + 1) + ' attempt failed')
            continue
        else:
            time.sleep(random.uniform(0.5, 1))
            # 使用模拟打字的方式发送消息
            lines = answer_message.split('\n')
            for i, line in enumerate(lines):
                if i > 0:  # 如果不是第一行，先发送换行
                    wx.SendKeys('{Shift}{Enter}', waitTime=0)
                    time.sleep(random.uniform(0.2, 0.5))
                send_message_with_typing(line)
                time.sleep(random.uniform(0.3, 0.6))  # 每行之间添加额外延迟
            
            time.sleep(random.uniform(0.5, 1))
            wx.SendKeys('{Enter}', waitTime=0)
            success = True
            Log(sender + answer_message)
            break
    if not success:
        time.sleep(random.uniform(1, 2))  # 增加延迟
        wx.SwitchToThisWindow()
        time.sleep(random.uniform(1, 2))  # 增加延迟
        send_message_with_typing('连接错误')
        time.sleep(random.uniform(0.5, 1))
        wx.SendKeys('{Enter}', waitTime=0)
        Log(sender + ' question connection failed')

def Log(log):
    log = str(log)
    print(log)
    log_file.write(log + '\n')

def send_status_message(target_user):
    """发送运行状态消息到指定用户"""
    # 增加切换聊天的随机延迟到1-2秒
    time.sleep(random.uniform(1, 2))
    # 切换到目标用户的聊天
    session.ButtonControl(Name=target_user).Click(simulateMove=False)
    time.sleep(random.uniform(1, 2))
    # 发送状态消息
    status_message = f"机器人正在正常运行中 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send_message_with_typing(status_message)
    time.sleep(random.uniform(0.5, 1))
    wx.SendKeys('{Enter}', waitTime=0)
    Log(f"已发送状态消息给 {target_user}")

def run_schedule():
    """运行定时任务"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

Log(str(datetime.now()) + '----------------------------------')
lines = open('./User_List.txt', encoding = 'utf-8').readlines()
allowed_senders = {}
for line in lines:
    line_content = line.replace('\n', '').split(',')
    if line_content[2] == 'me':
        me = line_content[0]
        continue
    elif line_content[2] == 'admin':
        admin.append(line_content[0])
    allowed_senders[line_content[0]] = [line_content[1], line_content[2]]

# 确保有管理员后再设置定时任务
if admin:
    status_receiver = admin[0]  # 使用第一个管理员
    schedule.every().day.at("06:00").do(send_status_message, status_receiver)
    
    # 启动定时任务线程
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
else:
    Log("警告：未找到管理员用户，状态通知功能未启动")

while True:
    time.sleep(0.1)
    new_message = session.TextControl(searchDepth=4)
    if not new_message.Exists(0):
        continue
    if new_message.Name:
        time.sleep(random.uniform(0.5, 1))
        wx.SwitchToThisWindow()
        time.sleep(random.uniform(0.5, 1))
        new_message.Click(simulateMove=False)
        message_sender = wx.ButtonControl(Name='聊天信息').GetParentControl().GetParentControl().GetParentControl().TextControl().Name
        if '(' in message_sender and ')' in message_sender:
            message_sender = message_sender[:message_sender.find('(')-1]
        if message_sender in allowed_senders:
            message = wx.ListControl(Name='消息').GetChildren()[-1].Name
            Log(message_sender + ': ' + message)
            if allowed_senders[message_sender][0] == 'individual':
                Reply_ChatGPT(new_message, message_sender, message)
            elif allowed_senders[message_sender][0] == 'group':
                prefix = '@' + me + '\u2005'
                if message.startswith(prefix):
                    Reply_ChatGPT(new_message, message_sender, message)