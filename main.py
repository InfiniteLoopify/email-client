import send
import receive
import gui
import os
from pathlib import Path

if __name__ == "__main__":

    username = "InfiniteLoopify@gmail.com"
    password = "gdpx xzah khyv vurg"
    labels = ['"[Gmail]/All Mail"', "Inbox", '"[Gmail]/Sent Mail"', '"[Gmail]/Trash"']

    receive = receive.Receive(username, password)
    send = send.Send(username, password)

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
        my_mail=username,
        send=send,
        receive=receive,
        labels=labels,
    )
    gui.sys.exit(app.exec_())
