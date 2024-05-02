import os
from pathlib import Path
from dotenv import load_dotenv

from email_client import send, receive, gui

load_dotenv()

if __name__ == "__main__":

    USERNAME = os.environ.get("EMAIL_USERNAME", "")
    PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
    labels = ['"[Gmail]/All Mail"', "Inbox", '"[Gmail]/Sent Mail"', '"[Gmail]/Trash"']

    receive = receive.Receive(USERNAME, PASSWORD)
    send = send.Send(USERNAME, PASSWORD)

    msgs = []
    file_name = "data/messages.data"

    Path(file_name).parent.mkdir(parents=True, exist_ok=True)
    if os.path.exists(file_name):
        msgs = gui.read_from_file(file_name)
    else:
        for label in labels:
            msgs.append(receive.get_message(category=label))

    app = gui.QApplication(gui.sys.argv)
    ex = gui.App(
        file_name=file_name,
        mails_lst=msgs,
        my_mail=USERNAME,
        send=send,
        receive=receive,
        labels=labels,
    )
    gui.sys.exit(app.exec_())
