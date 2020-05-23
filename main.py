import send
import receive
import gui
import time
import os


if __name__ == "__main__":

    username = "testcn98@gmail.com"
    password = "t1e2s3t4c5n6"
    labels = ['"[Gmail]/All Mail"', 'Inbox',
              '"[Gmail]/Sent Mail"',  '"[Gmail]/Trash"']

    # initialize smtp (email sending) and imap (email recieving) protocols
    receive = receive.Receive(username, password)
    send = send.Send(username, password)
    # send.send_message(username, "sadasd", "asdasdffasasfdsfa")

    msgs = []
    file_name = 'messages.data'
    # if msg file exists then read from it, else retreive msgs using imap
    if os.path.exists(file_name):
        msgs = gui.read_from_file(file_name)
    else:
        for label in labels:
            msgs.append(receive.get_message(category=label))

    # print inbox category only
    # for msg in msgs:
    #     print("To:\t", msg[1])
    #     print("Date:\t", msg[2])
    #     print("Subject:\t", msg[4])
    #     print("Content:\n", msg[5])
    #     print("_"*40)

    # load gui
    app = gui.QApplication(gui.sys.argv)
    ex = gui.App(mails_lst=msgs, my_mail=username,
                 send=send, receive=receive, labels=labels)
    gui.sys.exit(app.exec_())
