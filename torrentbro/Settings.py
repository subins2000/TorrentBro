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
        socks5 = settings.value('socks5')

        if socks5 == 'True':
            socks5_host = settings.value('socks5_host')
            socks5_port = settings.value('socks5_port')
            socks5_username = settings.value('socks5_username')
            socks5_password = settings.value('socks5_password')

            self.ui.hostInput.setText(socks5_host)
            self.ui.portInput.setText(socks5_port)
            self.ui.usernameInput.setText(socks5_username)
            self.ui.passwordInput.setText(socks5_password)

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
        socks5 = self.ui.torSettingsToggle.isChecked()
        socks5_host = self.ui.hostInput.text()
        socks5_port = self.ui.portInput.text()
        socks5_username = self.ui.usernameInput.text()
        socks5_password = self.ui.passwordInput.text()

        settings = QSettings('torrentbro', 'torrentbro')
        settings.setValue('socks5', str(socks5))
        settings.setValue('socks5_host', socks5_host)
        settings.setValue('socks5_port', socks5_port)
        settings.setValue('socks5_username', socks5_username)
        settings.setValue('socks5_password', socks5_password)

        del settings
