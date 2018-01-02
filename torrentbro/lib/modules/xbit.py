"""xbit.pw module."""

import logging
import sys
import time

import requests
from torrentbro.lib.utilities.Config import Config


class XBit(Config):
    """
    XBit class.

    This class fetches torrents from xbit.pw,
    and diplays results in tabular form.
    Further, torrent's magnetic link
    can be printed to console.
    Torrent can be added to client directly

    This class inherits Config class. Config class inherits
    Common class. The Config class provides proxies list fetched
    from config file. The Common class consists of commonly used
    methods.

    All activities are logged and stored in a log file.
    In case of errors/unexpected output, refer logs.
    """

    def __init__(self, title):
        """Initialisations."""
        Config.__init__(self)
        self.proxies = self.get_proxies('xbit')
        self.proxy = self.proxies[0]
        self.title = title
        self.logger = logging.getLogger('log1')
        self.class_name = self.__class__.__name__.lower()
        self.index = 0
        self.total_fetch_time = 0
        self.mapper = []
        self.mylist = []
        self.masterlist = []
        self.mylist_crossite = []
        self.masterlist_crossite = []
        self.data = {}
        self.headers = [
                'ID', 'NAME', 'INDEX', 'SIZE', 'DISCOVERED']

    def search_torrent(self):
        """
        Obtain and parse JSON.

        Torrent id, name, magnet, size and date are fetched.
        """
        try:
            search = "api?search=%s&limit=100" % (self.title)
            start_time = time.time()
            raw = requests.get(self.proxy+search).json()
            self.total_fetch_time = time.time() - start_time
            print("[in {:.2f} sec]".format(self.total_fetch_time))
            self.data = raw
            results = self.data['dht_results']
            if results == [{}]:
                return
            for result in results[:-1]:
                torrent_id = result['ID']
                name = result['NAME']
                magnet = result['MAGNET']
                size = result['SIZE']
                date = result['DISCOVERED']
                self.index += 1
                self.mapper.insert(self.index, (name, magnet, 'None', self.class_name))
                self.mylist = [torrent_id, name, "--"+str(self.index)+"--", size, date]
                self.masterlist.append(self.mylist)
                self.mylist_crossite = [name, self.index, size, '-1/-1', date]
                self.masterlist_crossite.append(self.mylist_crossite)
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" % (e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)


def main(title):
    """Execution begins here."""
    try:
        print("\n[XBit.pw]\n")
        xb = XBit(title)
        print("Using %s" %(xb.colorify("yellow", xb.proxy)))
        print("Fetching results...")
        xb.search_torrent()
        xb.post_fetch()
    except KeyboardInterrupt:
        xb.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


def cross_site(title, page_limit):
    xb = XBit(title)
    return xb


if __name__ == "__main__":
    print("It's a module!")
