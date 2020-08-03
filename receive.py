import email
import imaplib
import datetime
import re
# from pytz import timezone


class Receive:
    def __init__(self, username, password):
        print(f"initializing receive module for user {username}")

        imap_server = 'imap.gmail.com'
        # connect to the server and login
        self.mail = imaplib.IMAP4_SSL(imap_server, 993)
        self.mail.login(username, password)
        self.mail_content = []

    def get_message(self, category='inbox', date='', date_format='%a, %d %b %Y'):
        print(f"retrieving messages for catergory {category}")

        self.mail_content = []

        # select the category of mails to read
        self.mail.select(category)

        # search mails (all or after a date) and return status (OK or not) and mail ids
        if not date:
            status, data = self.mail.search(None, 'ALL')
        else:
            status, data = self.mail.search(None,  f'(SINCE "{date}")')

        # split data and convert bytes into list
        mail_ids = []
        for block in data:
            mail_ids += block.split()

        # for every mail id, extract its content
        for i in mail_ids:
            # fetch data and status for id, using specified format
            status, data = self.mail.fetch(i, '(RFC822)')

            for response_part in data:
                # if response_part is a tuple
                if isinstance(response_part, tuple):
                    # read message only (2nd element) of tuple
                    message = email.message_from_bytes(response_part[1])

                    # extract subject from the message
                    mail_subject = message['subject']
                    mail_subject = mail_subject.replace('\n', '')

                    # extract date from the message
                    mail_datetime = message['Date']

                    # extract all the from_addresses from the message
                    mail_from = message['from']
                    mail_from = re.findall(r'[\w\.-]+@[\w\.-]+', mail_from)

                    # extract all the to_addresses (to/cc/bcc) from the message
                    if message['to']:
                        mail_to = message['to']
                    elif message['Cc']:
                        mail_to = message['Cc']
                    elif message['Bcc']:
                        mail_to = message['Bcc']
                    else:
                        mail_to = ""
                    mail_to = re.findall(r'[\w\.-]+@[\w\.-]+', mail_to)

                    # if message contains non-text, then separate text from non-text
                    if message.is_multipart():
                        mail_content = ''

                        # loop through message types (text, html, images, attachments etc)
                        for part in message.get_payload():

                            # if the content type is text/plain, then extract it
                            if part.get_content_type() == 'text/plain':
                                mail_content += part.get_payload()
                    else:
                        # if the message isn't multipart, just extract it
                        mail_content = message.get_payload()

                    # convert date/time to correct local timezone and format
                    mail_datetime = mail_datetime.split('(')[0]
                    if mail_datetime[-1] == " ":
                        mail_datetime = mail_datetime[0:-1]
                    if "GMT" in mail_datetime:
                        mail_datetime = mail_datetime.replace("GMT", "+0700")
                    elif "UTC" in mail_datetime:
                        mail_datetime = mail_datetime.replace("UTC", "+0700")
                    mail_datetime = datetime.datetime.strptime(
                        mail_datetime, "%a, %d %b %Y %H:%M:%S %z")
                    local_timzone = datetime.datetime.now(
                        datetime.timezone.utc).astimezone().tzinfo
                    mail_datetime = mail_datetime.astimezone(
                        local_timzone)
                    mail_datetime = mail_datetime.strftime(
                        f'{date_format}|Today, %I:%M %p')

                    # split date and time from datetime string
                    mail_datetime = mail_datetime.split("|")
                    mail_date = mail_datetime[0]
                    mail_time = mail_datetime[1]

                    # append from, to, date, time, subject and content to message
                    self.mail_content.append(
                        [mail_from, mail_to, mail_date, mail_time, mail_subject,  mail_content])
        return self.mail_content


if __name__ == "__main__":
    username = "abc"
    password = "123"

    receive = Receive(username, password)

    cat = '"[Gmail]/Sent Mail"'
    msgs = receive.get_message(category=cat)
    print(msgs)

    # msgs = receive.mail.list()
    # receive.get_message(date="01-Jan-2021")
