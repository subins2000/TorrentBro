"""RarBg Module."""

import logging
import sys
import time

import requests
from torrentbro.lib.utilities.Config import Config


class RarBg(Config):
    """
    RarBg Class.

    Torrench uses RarBG API instead of scrapping the web.
    For this to work, a token is generated.
    Tokens automaticly expire in 15 minutes.
    The api has a 1req/2s limit.
    """
    def __init__(self, title):
        """Initialisations."""
        Config.__init__(self)
        self.proxies = self.get_proxies('rarbg')
        self.proxy = self.proxies[0]
        self.title = title
        self.logger = logging.getLogger('log1')
        self.class_name = self.__class__.__name__.lower()
        self.index = 0
        self.raw = None
        self.token = None
        self.mapper = []
        self.mylist = []
        self.masterlist = []
        self.mylist_crossite = []
        self.masterlist_crossite = []
        self.total_fetch_time = 0
        self.headers = [
                'CATEG', 'NAME', 'INDEX', 'SIZE', 'S/L', 'DATE'
                ]

    def get_token(self):
        """To generate token."""
        self.logger.debug("Getting token")
        get_token = "get_token=get_token"
        raw = requests.get(self.proxy+get_token).json()
        self.token = raw['token']
        self.logger.debug("Token generated - {}".format(self.token))

    def search_torrent(self):
        """To search torrent for given input.

        The API gives out results in JSON format.
        """
        try:
            params = "mode=search&app_id=torrench&sort=seeders&limit=100&format=json_extended&search_string={}&token={}".format(self.title, self.token)
            start_time = time.time()
            self.logger.debug("Fetching results")
            self.raw = requests.get(self.proxy+params).json()
            if 'error' in self.raw:
                return
            self.total_fetch_time = time.time() - start_time
            results = self.raw['torrent_results']
            for result in results:
                name = result['title']
                category = result['category']
                magnet = result['download']
                seeds = str(result['seeders'])
                leeches = str(result['leechers'])
                seeds_color = self.colorify("green", seeds)
                leeches_color = self.colorify("red", leeches)
                size = result['size']
                date = result['pubdate']
                date = " ".join(date.split(" ")[0:2])
                link = result['info_page']
                size = size/1024/1024/1024
                size_end = "GB"
                if size < 1:
                    size *= 1024
                    size_end = "MB"
                size = "{0:.2f} {1}".format(size, size_end)
                self.mapper.insert(self.index, (name, magnet, link, self.class_name))
                self.index += 1
                self.mylist = [category, name, "--" +
                    str(self.index) + "--", size, seeds_color + '/' + leeches_color, date]
                self.masterlist.append(self.mylist)
                self.mylist_crossite = [name, self.index, size, seeds+'/'+leeches, date]
                self.masterlist_crossite.append(self.mylist_crossite)
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" % (e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)


def main(title):
    """Execution begins here."""
    print("\n[RarBg]\n")
    rbg = RarBg(title)
    rbg.get_token()
    time.sleep(0.75)
    rbg.search_torrent()
    rbg.post_fetch()


def cross_site(title, page_limit):
    rbg = RarBg(title)
    rbg.get_token()
    time.sleep(0.75)
    return rbg


if __name__ == "__main__":
    print("It's a module!")
