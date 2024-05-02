import smtplib
import ssl
from email.mime.text import MIMEText


class Send:

    def __init__(self, username, password):
        print(f"initializing send module for user {username}")

        self.username = username
        self.password = password

        smtp_ssl_host = "smtp.gmail.com"
        smtp_ssl_port = 465
        # (25, 587) port for unencrypted

        self.server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        self.server.login(self.username, self.password)

    def send_message(self, to_address, subject, message):
        print(f"sending message(s) to {to_address}")
        if to_address == []:
            return

        msg = MIMEText(message)
        msg["subject"] = subject
        msg["from"] = self.username
        msg["to"] = ", ".join(to_address)

        self.server.sendmail(self.username, to_address, msg.as_string())

    def close(self):
        self.server.quit()


if __name__ == "__main__":
    username = "abc"
    password = "123"

    to = []
    sub = "Hello"
    msg = "This is a Project"

    mail = Send(username, password)
    mail.send_message(to, sub, msg)
    mail.close()
