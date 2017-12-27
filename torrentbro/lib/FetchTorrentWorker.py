'''
Handles torrent search
'''

import urllib

from PyQt5.QtCore import QObject, pyqtSignal

from torrentbro.lib.tpb import TPB
from torrentbro.lib.tpb.tpb import HitCloudflare


class FetchTorrentWorker(QObject):

    action = None
    values = []
    runs = True

    finished = pyqtSignal(str, object)

    def __init__(self, action, *values):
        super().__init__()

        self.action = action
        self.values = values
        self.runs = True

    def stop(self):
        self.runs = False

    def isStopped(self):
        return not self.runs

    def _search(self):
        searchQuery = self.values[0]

        try:

            self.tpb = TPB('https://thepiratebay.org')
            torrents = self.tpb.search(searchQuery)

            if self.isStopped():
                return

            torrentCount = 0
            for torrent in torrents:
                torrentCount += 1
                self.finished.emit('searchResultItem', torrent)

            self.finished.emit('searchResultSummary', torrentCount)

        except urllib.error.URLError as e:
            self.finished.emit('error', str(e.reason))
        except HitCloudflare:
            self.finished.emit('error', 'Hit cloudflare protection page.')

    def _torrentDetailedInfo(self):
        torrent = self.values[0]

        try:

            files = torrent.files

            if self.isStopped():
                return

            self.finished.emit('torrentInfoFiles', files)

            description = torrent.info

            if self.isStopped():
                return

            self.finished.emit('torrentInfoDescription', description)

        except urllib.error.URLError as e:
            self.finished.emit('error', str(e.reason))
        except HitCloudflare:
            self.finished.emit('error', 'Hit cloudflare protection page.')

    def run(self):
        '''
        Call functions that start with '_'
        '''
        actionFunction = getattr(self, '_' + self.action)
        actionFunction()
