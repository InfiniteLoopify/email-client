import email
import imaplib
import datetime
import re


class Receive:
    def __init__(self, username, password):
        print(f"initializing receive module for user {username}")

        imap_server = "imap.gmail.com"
        self.mail = imaplib.IMAP4_SSL(imap_server, 993)
        self.mail.login(username, password)
        self.mail_content = []

    def get_message(self, category="inbox", date="", date_format="%a, %d %b %Y"):
        print(f"retrieving messages for catergory {category}")

        self.mail_content = []

        self.mail.select(category)

        if not date:
            status, data = self.mail.search(None, "ALL")
        else:
            status, data = self.mail.search(None, f'(SINCE "{date}")')

        mail_ids = []
        for block in data:
            mail_ids += block.split()

        for i in mail_ids:
            status, data = self.mail.fetch(i, "(RFC822)")

            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])

                    mail_subject = message["subject"]
                    mail_subject = mail_subject.replace("\n", "")

                    mail_datetime = message["Date"]

                    mail_from = message["from"]
                    mail_from = re.findall(r"[\w\.-]+@[\w\.-]+", mail_from)

                    if message["to"]:
                        mail_to = message["to"]
                    elif message["Cc"]:
                        mail_to = message["Cc"]
                    elif message["Bcc"]:
                        mail_to = message["Bcc"]
                    else:
                        mail_to = ""
                    mail_to = re.findall(r"[\w\.-]+@[\w\.-]+", mail_to)

                    if message.is_multipart():
                        mail_content = ""

                        for part in message.get_payload():

                            if part.get_content_type() == "text/plain":
                                mail_content += part.get_payload()
                    else:
                        mail_content = message.get_payload()

                    mail_datetime = mail_datetime.split("(")[0]
                    if mail_datetime[-1] == " ":
                        mail_datetime = mail_datetime[0:-1]
                    if "GMT" in mail_datetime:
                        mail_datetime = mail_datetime.replace("GMT", "+0700")
                    elif "UTC" in mail_datetime:
                        mail_datetime = mail_datetime.replace("UTC", "+0700")
                    mail_datetime = datetime.datetime.strptime(
                        mail_datetime, "%a, %d %b %Y %H:%M:%S %z"
                    )
                    local_timzone = (
                        datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
                    )
                    mail_datetime = mail_datetime.astimezone(local_timzone)
                    mail_datetime = mail_datetime.strftime(
                        f"{date_format}|Today, %I:%M %p"
                    )

                    mail_datetime = mail_datetime.split("|")
                    mail_date = mail_datetime[0]
                    mail_time = mail_datetime[1]

                    self.mail_content.append(
                        [
                            mail_from,
                            mail_to,
                            mail_date,
                            mail_time,
                            mail_subject,
                            mail_content,
                        ]
                    )
        return self.mail_content


if __name__ == "__main__":
    username = "abc"
    password = "123"

    receive = Receive(username, password)

    cat = '"[Gmail]/Sent Mail"'
    msgs = receive.get_message(category=cat)
    print(msgs)
