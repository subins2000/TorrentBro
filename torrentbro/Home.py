#!/usr/bin/python3

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, qApp, QStyle, QDesktopWidget, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QTextBrowser

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

        searchButton = self.findChild(QPushButton, 'searchButton')
        searchButton.clicked.connect(self.onSearch)

        searchTextbox = self.findChild(QLineEdit, 'searchTextbox')
        searchTextbox.returnPressed.connect(self.onSearch)

    def initMenubar(self):
        quitAction = self.findChild(QAction, 'actionQuit')
        quitAction.triggered.connect(qApp.quit)

    def initIntro(self):
        torrentList = self.findChild(QListWidget, 'torrentList')
        torrentList.hide()

    def toggleListDisplay(self):
        torrentList = self.findChild(QListWidget, 'torrentList')
        torrentList.show()

        introText = self.findChild(QTextBrowser, 'introText')
        introText.hide()

    def onSearch(self):
        torrentList = self.findChild(QListWidget, 'torrentList')
        searchQuery = self.findChild(QLineEdit, 'searchTextbox').text()

        self.toggleListDisplay()

        tpb = TPB('https://thepiratebay.org')
        torrents = tpb.search(searchQuery)

        for torrent in torrents:
            torrentList.addItem(torrent.title)


if __name__ == '__main__':
    Home()
