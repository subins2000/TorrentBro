#!/usr/bin/python3

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, qApp, QStyle, QDesktopWidget, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QTextBrowser, QStatusBar

from tpb import TPB


class Home(QMainWindow):

    baseDir = None

    torrentListInfo = []

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

        self.searchButton.clicked.connect(self.onSearch)
        self.searchTextbox.returnPressed.connect(self.onSearch)
        self.torrentList.itemClicked.connect(self.onTorrentSelect)

    def initMenubar(self):
        self.quitAction.triggered.connect(qApp.quit)

    def initIntro(self):
        self.torrentList.hide()
        self.torrentInfo.hide()
        self.introText.show()

    def toggleListDisplay(self):
        self.introText.hide()
        self.torrentList.show()

    def onSearch(self):
        searchQuery = self.searchTextbox.text()

        self.toggleListDisplay()

        self.statusBar.showMessage('Searching')

        tpb = TPB('https://thepiratebay.org')
        torrents = tpb.search(searchQuery)

        for torrent in torrents:
            self.torrentListInfo.append(torrent)
            self.torrentList.addItem(torrent.title)

    def onTorrentSelect(self):
        selectedTorrentIndex = self.torrentList.currentRow()

        self.torrentInfo.setHtml(
            '''
            <h1>{title}</h1>
            '''.format(
                title=self.torrentListInfo[selectedTorrentIndex].title
            )
        )

        self.torrentInfo.show()


if __name__ == '__main__':
    Home()
