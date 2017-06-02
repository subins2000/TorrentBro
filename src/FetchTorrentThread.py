'''
Handles torrent search
'''

import urllib

from PyQt5.QtCore import QThread, pyqtSignal

from tpb import TPB


class FetchTorrentThread(QThread):

    action = None
    values = []
    runs = True

    finished = pyqtSignal(str, object)

    def __init__(self, action, *values):
        QThread.__init__(self)

        self.action = action
        self.values = values
        self.runs = True

    def __del__(self):
        self.wait()

    def stop(self):
        self.runs = False

    def checkIfStopped(self):
        if not self.runs:
            self.quit()
            self.wait()
            self.terminate()
            return True
        else:
            return False

    def _search(self):
        searchQuery = self.values[0]

        try:

            self.tpb = TPB('https://thepiratebay.org')
            torrents = self.tpb.search(searchQuery)

            if self.checkIfStopped():
                return

            torrentCount = 0
            for torrent in torrents:
                torrentCount += 1
                self.finished.emit('searchResultItem', torrent)

            self.finished.emit('searchResultSummary', torrentCount)

        except urllib.error.URLError as e:
            self.finished.emit('internetFailed', str(e.reason))

    def _torrentDetailedInfo(self):
        torrent = self.values[0]

        try:

            files = torrent.files

            if self.checkIfStopped():
                return

            self.finished.emit('torrentInfoFiles', files)

            description = torrent.info

            if self.checkIfStopped():
                return

            self.finished.emit('torrentInfoDescription', description)

        except urllib.error.URLError as e:
            self.finished.emit('internetFailed', str(e.reason))

    def run(self):
        '''
        Call functions that start with '_'
        '''
        actionFunction = getattr(self, '_' + self.action)
        actionFunction()
