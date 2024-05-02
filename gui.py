import re
import sys
import pickle
import threading

from datetime import date
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
    QMenuBar,
    QPushButton,
    QMenu,
    QToolBar,
    QAction,
    QMainWindow,
    QStatusBar,
    QMessageBox,
)


def read_from_file(filename):
    print(f"reading from file {filename}")
    with open(filename, "rb") as filehandle:
        data = pickle.load(filehandle)
    return data


def write_to_file(filename, data):
    print(f"writing to file {filename}")
    with open(filename, "wb") as filehandle:
        pickle.dump(data, filehandle)


class App(QWidget):

    FROM, TO, DATE, SUBJECT, MESSAGE = range(5)

    def __init__(
        self,
        file_name="messages.data",
        mails_lst=None,
        my_mail="",
        send=None,
        receive=None,
        labels=None,
    ):
        super().__init__()
        if mails_lst is None:
            mails_lst = []

        self.sendClass = send
        self.receiveClass = receive
        self.labelsClass = labels
        self.mails_lst = mails_lst
        self.mails = mails_lst[1]
        self.my_mail = my_mail
        self.labels = ["All", "Inbox", "Sent", "Trash"]
        self.title = "SMTP Email Client"
        self.left = 0
        self.top = 0
        self.width = 1024
        self.height = 600
        self.total_cols = 5
        self.ret_val = False
        self.is_first_ret_val = True
        self.is_reload_mails = False
        self.messages_file = file_name
        self.initUI()

    def toolbarButtonClick(self, i):
        def buttonClick():
            if self.send_button.isChecked():
                self.send_button.setChecked(False)
                self.sendMenuToggleClick(False)
            if self.label_buttons[i].isChecked():
                print(f"displaying label category '{self.labels[i]}'")
                for index, label_button in enumerate(self.label_buttons):
                    if index != i:
                        label_button.setChecked(False)
                self.mails = self.mails_lst[i]
                self.reloadMails()
            else:
                self.label_buttons[i].setChecked(True)

        return buttonClick

    def parallelReloading(self):
        temp_mails_lst = []
        for label in self.labelsClass:
            temp_mails_lst.append(self.receiveClass.get_message(category=label))
        index = [label.isChecked() for label in self.label_buttons].index(True)
        self.mails_lst = temp_mails_lst
        self.mails = temp_mails_lst[index]
        write_to_file(self.messages_file, self.mails_lst)
        self.is_reload_mails = True

    def parallelSending(self, to_addr, subj, msg):
        self.sendClass.send_message(to_addr, subj, msg)

    def reloadButtonClick(self, s):
        if self.receiveClass:
            if self.is_first_ret_val:
                print("reloading all mails")
                self.ret_val = threading.Thread(target=self.parallelReloading, args=())
                self.ret_val.start()
                self.is_first_ret_val = False
            elif not self.ret_val.is_alive():
                print("reloading all mails")
                self.ret_val = threading.Thread(target=self.parallelReloading, args=())
                self.ret_val.start()
            else:
                print("reloading already taking place in background")
        else:
            print("unable to reload as 'receiveClass' missing")
        self.reload_button.setChecked(False)

    def sendMenuToggleClick(self, s):
        if s:
            self.toBox.setFixedWidth(self.contentView.width())
            self.contentView.hide()
            self.toBox.show()
            self.subjectBox.show()
            self.messageBox.show()
            self.sendButtonBox.show()
        else:
            self.toBox.hide()
            self.subjectBox.hide()
            self.messageBox.hide()
            self.sendButtonBox.hide()
            self.contentView.show()

    def logoutButtonClick(self, s):
        print("loging out and closing app")
        sys.exit()

    def rowSelectionClick(self):
        if self.send_button.isChecked():
            self.send_button.setChecked(False)
            self.sendMenuToggleClick(False)
        self.dataView.showColumn(1)
        self.dataView.showColumn(4)
        item = self.dataView.selectedIndexes()
        lst = []
        for i in range(self.total_cols):
            text = item[i].model().itemFromIndex(item[i]).text()
            if i == 0 or i == 1:
                text = text.split()
            lst.append(text)
        self.dataView.hideColumn(1)
        self.dataView.hideColumn(4)

        msg = self.htmlString(lst)
        self.contentView.setPlainText("")
        self.contentView.textCursor().insertHtml(msg)

    def sendButtonClick(self):
        if self.sendClass:
            self.reloadButtonClick(True)
            to_addr = re.findall(r"[\w\.-]+@[\w\.-]+", self.toBox.text())
            subj = self.subjectBox.text()
            msg = self.messageBox.toPlainText()
            send_ret_val = threading.Thread(
                target=self.parallelSending, args=(to_addr, subj, msg)
            )
            send_ret_val.start()
        else:
            print("unable to send as 'sendClass' missing")
        self.toBox.setText("")
        self.subjectBox.setText("")
        self.messageBox.setPlainText("")
        self.sendMenuToggleClick(False)
        self.send_button.setChecked(False)

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.globalLayout = QVBoxLayout()
        menuLayout = QHBoxLayout()
        dataLayout = QHBoxLayout()

        labelLayout = QToolBar("Labels")
        self.label_buttons = [QAction(label, self) for label in self.labels]
        for i, label_button in enumerate(self.label_buttons):
            label_button.triggered.connect(self.toolbarButtonClick(i))
            labelLayout.addAction(label_button)
            label_button.setCheckable(True)
        self.label_buttons[1].setChecked(True)

        optionLayout = QToolBar("Options")
        self.send_button = QAction(
            QIcon("images/icons8-email-60.png"), "Send Mail", self
        )
        self.reload_button = QAction(
            QIcon("images/icons8-reset-60.png"), "Reload Page", self
        )
        logout_button = QAction(QIcon("images/icons8-shutdown-60.png"), "Logout", self)

        self.send_button.triggered.connect(self.sendMenuToggleClick)
        self.reload_button.triggered.connect(self.reloadButtonClick)
        logout_button.triggered.connect(self.logoutButtonClick)
        optionLayout.addAction(self.send_button)
        optionLayout.addAction(self.reload_button)
        optionLayout.addAction(logout_button)
        self.send_button.setCheckable(True)
        self.reload_button.setCheckable(True)
        logout_button.setCheckable(True)
        menuLayout.setContentsMargins(0, 0, 0, 0)
        optionLayout.setFixedWidth(106)
        menuLayout.addWidget(labelLayout, 10)
        menuLayout.addWidget(QLabel(self.my_mail), 1)
        menuLayout.addWidget(optionLayout)

        self.dataView = QTreeView()
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.contentView = QPlainTextEdit()
        self.contentView.setReadOnly(True)

        self.sendLayout = QVBoxLayout()
        self.toBox = QLineEdit()
        self.subjectBox = QLineEdit()
        self.messageBox = QPlainTextEdit()
        self.sendButtonBox = QPushButton("Send")
        self.toBox.setPlaceholderText("To")
        self.subjectBox.setPlaceholderText("Subject")
        self.messageBox.setPlaceholderText("Message")
        self.sendLayout.addWidget(self.toBox)
        self.sendLayout.addWidget(self.subjectBox)
        self.sendLayout.addWidget(self.messageBox)
        self.sendLayout.addWidget(self.sendButtonBox)
        self.sendLayout.setSpacing(0)
        self.sendLayout.setContentsMargins(0, 0, 0, 0)

        dataLayout.addWidget(self.dataView, 3)
        dataLayout.addWidget(self.contentView, 2)
        dataLayout.addLayout(self.sendLayout)
        self.contentView.show()
        self.toBox.hide()
        self.subjectBox.hide()
        self.messageBox.hide()
        self.sendButtonBox.hide()

        self.sendButtonBox.clicked.connect(self.sendButtonClick)

        self.model = self.createMailModel(self)
        self.dataView.setModel(self.model)
        self.dataView.clicked.connect(self.rowSelectionClick)

        self.globalLayout.addLayout(menuLayout, 1)
        self.globalLayout.addLayout(dataLayout, 20)
        self.setLayout(self.globalLayout)

        self.addAllMails()
        self.autoColumnWidths()
        self.show()

        self.reloadButtonClick(True)

    def reloadMails(self):
        self.model.removeRows(0, self.model.rowCount())
        self.addAllMails()
        self.autoColumnWidths()

    def createMailModel(self, parent):
        model = QStandardItemModel(0, self.total_cols, parent)
        model.setHeaderData(self.FROM, Qt.Horizontal, "From")
        model.setHeaderData(self.TO, Qt.Horizontal, "To")
        model.setHeaderData(self.DATE, Qt.Horizontal, "Date")
        model.setHeaderData(self.SUBJECT, Qt.Horizontal, "Subject")
        model.setHeaderData(self.MESSAGE, Qt.Horizontal, "Message")
        return model

    def addAllMails(self):
        today = date.today()
        today_date = today.strftime("%a, %d %b %Y")
        for mail in self.mails:
            if today_date == mail[2]:
                date_temp = mail[3]
            else:
                date_temp = mail[2]
            self.addMail(self.model, mail[0], mail[1], date_temp, mail[4], mail[5])
        if self.mails:
            msg = self.htmlString(self.mails[-1])
            self.contentView.setPlainText("")
            self.contentView.textCursor().insertHtml(msg)

    def addMail(self, model, mailFrom, mailTo, date, subject, message):
        model.insertRow(0)
        mailFrom = " ".join(map(str, mailFrom))
        mailTo = " ".join(map(str, mailTo))
        model.setData(model.index(0, self.FROM), mailFrom)
        model.setData(model.index(0, self.TO), mailTo)
        model.setData(model.index(0, self.DATE), date)
        model.setData(model.index(0, self.SUBJECT), subject)
        model.setData(model.index(0, self.MESSAGE), message)

    def autoColumnWidths(self):
        width_plus = 30
        self.dataView.setColumnWidth(1, 0)
        self.dataView.setColumnWidth(4, 0)
        for i in range(self.total_cols):
            self.dataView.resizeColumnToContents(i)
            width = self.dataView.columnWidth(i)
            self.dataView.setColumnWidth(i, width + width_plus)
        self.dataView.hideColumn(1)
        self.dataView.hideColumn(4)

    def htmlString(self, lst):
        fr_addr = "<b>From</b><br>"
        for l in lst[0]:
            fr_addr += f"{l}<br>"
        fr_addr += "<br>"

        to_addr = "<b>To</b><br>"
        for l in lst[1]:
            to_addr += f"{l}<br>"
        to_addr += "<br>"

        subject = f"<b>Subject</b><br>{lst[-2]}<br><br>"
        message = lst[-1].replace("\n", "<br>")
        message = f"<b>Message</b><br>{message}<br><br>"
        return fr_addr + to_addr + subject + message


if __name__ == "__main__":

    msg = read_from_file("messages.data")
    app = QApplication(sys.argv)
    ex = App(msg, my_mail="abc@gmail.com")
    sys.exit(app.exec_())
