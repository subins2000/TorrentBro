#!/usr/bin/python3

import datetime
import os
import subprocess
import sys

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, qApp, QStyle, QDesktopWidget, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QTextBrowser, QStatusBar

from FetchTorrentThread import *
from ui import *
from utils import *


class Home(QMainWindow):

    baseDir = None

    torrentListInfo = []

    FTT = None

    def __init__(self):
        super().__init__()

        self.initUI()
        self.initMenubar()
        self.initIntro()

    def initUI(self):
        self.ui = Ui_Home()
        self.ui.setupUi(self)

        self.setGeometry(
            QStyle.alignedRect(
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                qApp.desktop().availableGeometry()
            )
        )
        self.show()

        self.ui.searchButton.clicked.connect(self.onSearch)
        self.ui.searchTextbox.returnPressed.connect(self.onSearch)

        self.ui.torrentList.selectionModel().selectionChanged.connect(self.onTorrentSelect)

        self.ui.torrentInfoMagnetLink.linkActivated.connect(self.onLinkClick)
        self.ui.torrentInfoTorrentLink.linkActivated.connect(self.onLinkClick)

    def initMenubar(self):
        self.ui.quitAction.triggered.connect(qApp.quit)

    def initIntro(self):
        self.ui.torrentList.hide()
        self.ui.torrentInfo.hide()
        self.ui.introText.show()

    def toggleListDisplay(self):
        self.ui.introText.hide()
        self.ui.torrentList.show()

    def onSearch(self):
        searchQuery = self.ui.searchTextbox.text()

        if not searchQuery:
            self.ui.statusBar.showMessage('Please type in something')

        self.toggleListDisplay()
        self.ui.torrentInfo.hide()

        self.ui.torrentList.clear()
        self.ui.torrentListInfo = []

        self.ui.statusBar.showMessage('Searching')

        self.stopFTT()

        self.FTT = FetchTorrentThread('search', searchQuery)
        self.FTT.finished.connect(self.threadOnResponse)
        self.FTT.start()

    '''
    Handle response from thread
    '''

    def threadOnResponse(self, action, *result):
        if (action == 'searchResultItem'):
            torrent = result[0]

            self.ui.torrentList.addItem(torrent.title)
            self.ui.torrentListInfo.append(torrent)

        elif (action == 'internetFailed'):
            self.ui.statusBar.showMessage(
                'Internet operation failed - ' + result[0])

        elif (action == 'searchResultSummary'):
            resultCount = result[0]

            if(resultCount == 0):
                self.ui.statusBar.showMessage('No results found')
            else:
                self.ui.statusBar.showMessage(
                    'Showing ' + str(resultCount) + ' results')

        elif (action == 'torrentInfoFiles'):
            files = result[0]

            if len(files) == 0:
                self.ui.torrentInfoFiles.setText('File list not available')
            else:
                fileList = ''

                for file in files:
                    fileList += '- ' + file + '<br/>'

                self.ui.torrentInfoFiles.setText(fileList)

        elif (action == 'torrentInfoDescription'):
            description = result[0].replace('\n', '<br/>')

            self.ui.torrentInfoDescription.setHtml(Linkify(description).getResult())

    '''
    Stop the thread
    '''

    def stopFTT(self):
        if (self.FTT != None):
            self.FTT.stop()

    '''
    On selecting a torrent from list
    '''

    def onTorrentSelect(self):
        selectedTorrentIndex = self.ui.torrentList.currentRow()
        torrent = self.ui.torrentListInfo[selectedTorrentIndex]

        self.stopFTT()

        self.FTT = FetchTorrentThread('torrentDetailedInfo', torrent)
        self.FTT.finished.connect(self.threadOnResponse)
        self.FTT.start()

        '''
        Clear files list and description
        '''
        self.ui.torrentInfoDescription.setText('')
        self.ui.torrentInfoFiles.setText('')

        self.ui.torrentInfoBasic.setHtml(
            '''
            <h1>{title}</h1>
            <p>{category} -> {sub_category}</p>
            <p>Seeders : <b>{seeders}</b>, Leechers : <b>{leechers}</b></p>
            <p>Size : <b>{size}</b></p>
            <p>Uploaded by <b>{username}</b> on <b>{created}</b></p>
            '''.format(
                title=torrent.title,
                category=torrent.category,
                sub_category=torrent.sub_category,
                seeders=torrent.seeders,
                leechers=torrent.leechers,
                size=torrent.size,
                username=torrent.user,
                created=torrent.created
            )
        )

        self.ui.torrentInfoMagnetLink.setText(
            '''
            <a href='{magnet_link}'>Magnet Link</a>
            '''.format(
                magnet_link=torrent.magnet_link
            )
        )

        if (torrent.torrent_link == None):
            self.ui.torrentInfoTorrentLink.setText('Torrent File Link')
            self.ui.torrentInfoTorrentLink.setToolTip(
                'The torrent site does not provide .torrent file')
        else:
            self.ui.torrentInfoTorrentLink.setText(
                '''
                <a href='{torrent_link}'>Torrent File Link</a>
                '''.format(
                    torrent_link=torrent.torrent_link
                )
            )
            self.ui.torrentInfoTorrentLink.setToolTip('Link to .torrent file')

        self.ui.torrentInfo.show()

    def onLinkClick(self, url):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', url))
        elif os.name == 'nt':
            os.startfile(url)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', url))


if __name__ == '__main__':
    Home()
