import smtplib
from email.mime.text import MIMEText

def send_email(to_email, code):
    smtp_server = "smtp.qq.com"
    smtp_port = 587  # TLS
    sender_email = "1327470638@qq.com"
    sender_auth_code = "miwjwkcdcinpicih"

    subject = "验证码"
    body = f"【扇贝单词】您的验证码是：{code}。\n如非本人操作，请忽略此邮件。"

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_auth_code)
        server.sendmail(sender_email, [to_email], message.as_string())
        server.quit()
        print(f"✅ 验证码 {code} 已发送至 {to_email}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False
