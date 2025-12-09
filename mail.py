# 发邮件
# 负责发送邮件
import smtplib
# 负责构造邮件的正文
from email.mime.text import MIMEText
# 负责邮件的标题
from email.header import Header


import sys
 
# 发送邮箱的服务器
smtpserver = 'smtp.163.com'
# 发送邮箱用户、授权密码非登录密码
user = '18217272676@163.com'
password = 'FY123456'
 
# 发送的邮箱
sender = '18217272676@163.com'
# 接受的邮箱
receiver = sys.argv[1]

timeVar = sys.argv[2] 

 
# 发送邮件主题，不能有test，否则会发不出去
subject = 'RBPsuite result (JOB-ID: ' + timeVar + ')'


 
# 发送的附件

mail_msg = """
<h2>Thank you for use RBPsuite server!</h2>
<p>Please view your result at <a style=\"font-size:20px\"; href="http://www.csbio.sjtu.edu.cn/bioinf/RBPsuite/result/
"""+timeVar.strip(" ")+"""\">RESULT</a></p>"""

message = MIMEText(mail_msg, 'html', 'utf-8')
message['Subject'] = subject
message['from'] = 'RBPsuite Server<18217272676@163.com>'
message['to'] = sys.argv[1]

 
 
# 连接发送邮件
try:
	smtp = smtplib.SMTP()
	smtp.connect(smtpserver)
	smtp.login(user, password)
	smtp.sendmail(sender, receiver, message.as_string())
	smtp.quit()
	print("Success!")
except smtplib.SMTPException:
    print ("Error: 无法发送邮件")

	
