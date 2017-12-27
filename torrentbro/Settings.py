#!/usr/bin/python3

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog

from torrentbro.ui import Ui_Settings

class Settings(QDialog):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.initEvents()

        self.exec_()
        self.show()

    def initUI(self):
        self.ui = Ui_Settings()
        self.ui.setupUi(self)

        settings = QSettings('torrentbro', 'torrentbro')
        socks5_host = settings.value('socks5_host')

        if socks5_host:
            socks5_port = settings.value('socks5_port')

            self.ui.hostInput.setPlainText(socks5_host)
            self.ui.portInput.setPlainText(socks5_port)

            self.ui.torSettingsToggle.setChecked(True)
            self.ui.torSettings.show()
        else:
            self.ui.torSettingsToggle.setChecked(False)
            self.ui.torSettings.hide()

    def initEvents(self):
        self.ui.buttonBox.accepted.connect(self.onOk)
        self.ui.torSettingsToggle.stateChanged.connect(self.onTorSettingsToggle)

    def onTorSettingsToggle(self):
        if self.ui.torSettingsToggle.isChecked():
            self.ui.torSettings.show()
        else:
            self.ui.torSettings.hide()

    def onOk(self):
        socks5_host = self.ui.hostInput.toPlainText()
        socks5_port = self.ui.portInput.toPlainText()

        settings = QSettings('torrentbro', 'torrentbro')
        settings.setValue('socks5_host', socks5_host)
        settings.setValue('socks5_port', socks5_port)

        del settings
