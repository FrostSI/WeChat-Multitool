import time
from datetime import datetime
import uiautomation
from openai import OpenAI

wx = uiautomation.WindowControl(ClassName='WeChatMainWndForPC')
session = wx.ListControl(Name='会话')
client = OpenAI(api_key = open('./API_KEY.txt').readline(), base_url="https://api.moonshot.cn/v1")
log_file = open('./log.txt', 'a', encoding='utf-8')
me = ''
admin = []

def Reply_ChatGPT(message_window, sender, question_message):
    success = False
    wx.SwitchToThisWindow()
    message_window.Click(simulateMove=False)
    wx.SendKeys(text='让我想想', waitTime=0)
    wx.SendKeys('{Enter}', waitTime=0)
    for tries in range(3):
        try:
            answer_message = client.chat.completions.create(model="moonshot-v1-8k", messages=[{"role": "user", "content": question_message}]).choices[0].message.content
        except:
            Log(sender + ' ' + str(tries + 1) + ' attempt failed')
            continue
        else:
            wx.SendKeys(text = answer_message.replace('\n', '{Shift}{Enter}'), waitTime = 0)
            wx.SendKeys('{Enter}', waitTime = 0)
            success = True
            Log(sender + answer_message)
            break
    if not success:
        wx.SwitchToThisWindow()
        wx.SendKeys(text='连接错误', waitTime=0)
        wx.SendKeys('{Enter}', waitTime=0)
        Log(sender + ' question connection failed')

def Log(log):
    log = str(log)
    print(log)
    log_file.write(log + '\n')

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

while True:
    time.sleep(0.1)
    new_message = session.TextControl(searchDepth=4)
    if not new_message.Exists(0):
        continue
    if new_message.Name:
        wx.SwitchToThisWindow()
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