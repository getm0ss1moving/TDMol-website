#!/usr/bin/env python3
"""
send_email.py - 发送EDM结果邮件
参数:
    sys.argv[1] = email (接收邮箱)
    sys.argv[2] = task_id
"""

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys

# 发送邮箱的服务器
smtpserver = 'smtp.163.com'
# 发送邮箱用户、授权密码
user = '18217272676@163.com'
password = 'FY123456'

# 发送的邮箱
sender = '18217272676@163.com'
# 接受的邮箱
receiver = sys.argv[1]

task_id = sys.argv[2]

# 发送邮件主题
subject = 'TDmol Generation Result (JOB-ID: ' + task_id + ')'

# 邮件正文
mail_msg = """
<h2>Thank you for using TDmol Generator!</h2>
<p>Your molecule generation task has been completed successfully.</p>
<p>Please view your results at <a style="font-size:20px"; href="http://www.csbio.sjtu.edu.cn/bioinf/TDMol/result/""" + task_id.strip(" ") + """_brief.html">VIEW RESULTS</a></p>
<p><strong>Task ID:</strong> """ + task_id + """</p>
<p>If you have any questions, please contact our support team.</p>
<br>
<p>Best regards,<br>EDM Server Team</p>
"""

message = MIMEText(mail_msg, 'html', 'utf-8')
message['Subject'] = subject
message['from'] = 'EDM Server<18217272676@163.com>'
message['to'] = receiver

# 连接发送邮件
try:
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(user, password)
    smtp.sendmail(sender, receiver, message.as_string())
    smtp.quit()
    print(f"Email sent successfully to {receiver}")
except smtplib.SMTPException as e:
    print(f"Error: Unable to send email - {e}")
