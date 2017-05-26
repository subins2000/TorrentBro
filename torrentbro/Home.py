#!/usr/bin/python3

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, qApp, QStyle, QDesktopWidget, QListWidget, QListWidgetItem

from tpb import TPB


class Home(QMainWindow):

    baseDir = None

    def __init__(self, baseDir):
        super().__init__()

        self.baseDir = baseDir
        self.initUI()
        self.initMenubar()
        self.initIntro()

    def initUI(self):
        uic.loadUi(self.baseDir + '/ui/Home.ui', self)

        self.setGeometry(
            QStyle.alignedRect(
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                qApp.desktop().availableGeometry()
            )
        )
        self.show()

    def initMenubar(self):
        quitAction = self.findChild(QAction, 'actionQuit')
        quitAction.triggered.connect(qApp.quit)

    def initIntro(self):
        torrentList = self.findChild(QListWidget, 'torrentList')
        torrentList.hide()


if __name__ == '__main__':
    Home()
