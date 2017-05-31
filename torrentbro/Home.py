#!/usr/bin/python3

import os
import subprocess
import sys

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, qApp, QStyle, QDesktopWidget, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QTextBrowser, QStatusBar

from FetchTorrentThread import *


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

        self.torrentInfoMagnetLink.linkActivated.connect(self.onLinkClick)
        self.torrentInfoTorrentLink.linkActivated.connect(self.onLinkClick)

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

        self.torrentList.clear()
        self.torrentListInfo = []

        self.statusBar.showMessage('Searching')

        self.FTT = FetchTorrentThread('search', searchQuery)
        self.FTT.finished.connect(self.threadOnResponse)
        self.FTT.start()

    def threadOnResponse(self, action, *result):
        if (action == 'searchResultItem'):
            torrent = result[0]

            self.torrentList.addItem(torrent.title)
            self.torrentListInfo.append(torrent)

        elif (action == 'searchFailed'):
            self.statusBar.showMessage('Search failed - ' + result[0])

        elif (action == 'searchResultSummary'):
            self.statusBar.showMessage(
                'Showing ' + str(result[0]) + ' results')

    def onTorrentSelect(self):
        selectedTorrentIndex = self.torrentList.currentRow()
        torrent = self.torrentListInfo[selectedTorrentIndex]

        self.torrentInfoBasic.setHtml(
            '''
            <h1>{title}</h1>
            <p>{category} -> {sub_category}</p>
            <p>Seeders : {seeders}</p>
            <p>Leechers : {leechers}</p>
            '''.format(
                title=torrent.title,
                category=torrent.category,
                sub_category=torrent.sub_category,
                seeders=torrent.seeders,
                leechers=torrent.leechers
            )
        )

        self.torrentInfoMagnetLink.setText(
            '''
            <a href='{magnet_link}'>Magnet Link</a>
            '''.format(
                magnet_link=torrent.magnet_link
            )
        )

        self.torrentInfoTorrentLink.setText(
            '''
            <a href='{torrent_link}'>Torrent File Link</a>
            '''.format(
                torrent_link=torrent.torrent_link
            )
        )

        self.torrentInfo.show()

    def onLinkClick(self, url):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', url))
        elif os.name == 'nt':
            os.startfile(url)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', url))


if __name__ == '__main__':
    Home()
