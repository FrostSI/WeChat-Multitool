import time
import uiautomation
from openai import OpenAI

wx = uiautomation.WindowControl(ClassName='WeChatMainWndForPC')
session = wx.ListControl(Name='会话')
client = OpenAI(api_key = open('./API_KEY.txt').readline())
me = ''
admin = []

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

print(allowed_senders)

def Reply_ChatGPT(question_message):
    success = False
    for tries in range(3):
        try:
            answer_message = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": question_message}]).choices[0].message.content
        except:
            print(message_sender + ' ' + str(tries + 1) + ' attempt failed')
            continue
        else:
            wx.SwitchToThisWindow()
            wx.SendKeys(text=answer_message, waitTime=0)
            wx.SendKeys('{Enter}', waitTime=0)
            success = True
            break
    if not success:
        wx.SwitchToThisWindow()
        wx.SendKeys(text='连接错误', waitTime=0)
        wx.SendKeys('{Enter}', waitTime=0)

while True:
    time.sleep(1)
    new_message = session.TextControl(searchDepth=4)
    if not new_message.Exists(0):
        continue
    if new_message.Name:
        wx.SwitchToThisWindow()
        print('接收到新消息')
        new_message.Click(simulateMove=False)
        message_sender = wx.ButtonControl(Name='聊天信息').GetParentControl().GetParentControl().GetParentControl().TextControl().Name
        if message_sender.find('(') and message_sender.find(')'):
            message_sender = message_sender[:message_sender.find('(')-1]
        print('消息发送者: ' + message_sender + '所有消息发送者：' + allowed_senders)
        if message_sender in allowed_senders:
            message = wx.ListControl(Name='消息').GetChildren()[-1].Name
            print('发送者: ' + message_sender + '消息: ' + message)
            if allowed_senders[message_sender][0] == 'individual':
                Reply_ChatGPT(message)
            elif allowed_senders[message_sender][0] == 'group':
                prefix = '@' + me + ' '
                if message.find(prefix):
                    Reply_ChatGPT(message)