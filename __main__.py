import time
import uiautomation
from openai import OpenAI

wx = uiautomation.WindowControl(ClassName='WeChatMainWndForPC')
session = wx.ListControl(Name='会话')
client = OpenAI(api_key='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')

allowed_senders = ['云中的鸟']

while True:
    time.sleep(1)
    new_message = session.TextControl(searchDepth=4)
    if not new_message.Exists(0):
        continue
    if new_message.Name:
        wx.SwitchToThisWindow()
        new_message.Click(simulateMove=False)
        message_sender = wx.ButtonControl(Name='聊天信息').GetParentControl().GetParentControl().GetParentControl().TextControl().Name
        if message_sender in allowed_senders:
            question_message = wx.ListControl(Name='消息').GetChildren()[-1].Name
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