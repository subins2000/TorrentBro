'''
Handles torrent search
'''

import urllib

from PyQt5.QtCore import QThread, pyqtSignal

from tpb import TPB


class FetchTorrentThread(QThread):

    action = None
    values = []

    finished = pyqtSignal(str, object)

    def __init__(self, action, *values):
        QThread.__init__(self)

        self.action = action
        self.values = values

    def __del__(self):
        self.wait()

    def _search(self):
        searchQuery = self.values[0]

        try:
            tpb = TPB('https://thepiratebay.org')
            torrents = tpb.search(searchQuery)

            torrentCount = 0
            for torrent in torrents:
                torrentCount += 1
                self.finished.emit('searchResultItem', torrent)

            self.finished.emit('searchResultSummary', torrentCount)

        except urllib.error.URLError as e:
            self.finished.emit('searchFailed', str(e.reason))

    def run(self):
        '''
        Call functions that start with '_'
        '''
        actionFunction = getattr(self, '_' + self.action)
        actionFunction()
