"""KickassTorrents Module."""

import logging
import sys

from torrentbro.lib.utilities.Config import Config


class KickassTorrents(Config):
    """
    KickassTorrent class.

    This class fetches torrents from KAT proxy,
    and diplays results in tabular form.
    Further, torrent's magnetic link and
    upstream link can be printed on console.
    Torrent can be added to client directly
    (still needs tweaking. may not work as epected)

    This class inherits Config class. Config class inherits
    Common class. The Config class provides proxies list fetched
    from config file. The Common class consists of commonly used
    methods.

    All activities are logged and stored in a log file.
    In case of errors/unexpected output, refer logs.
    """

    def __init__(self, title, page_limit):
        """Initialisations."""
        Config.__init__(self)
        self.proxies = self.get_proxies('kat')
        self.title = title
        self.pages = page_limit
        self.logger = logging.getLogger('log1')
        self.class_name = self.__class__.__name__.lower()
        self.page = 0
        self.proxy = None
        self.soup = None
        self.soup_dict = {}
        self.index = 0
        self.total_fetch_time = 0
        self.mapper = []
        self.mylist = []
        self.masterlist = []
        self.mylist_crossite = []
        self.masterlist_crossite = []
        self.headers = [
                'CATEG', 'NAME', 'INDEX', 'UPLOADER', 'SIZE', 'DATE', 'SE/LE', 'C']

    def check_proxy(self):
        """
        To check proxy availability.

        Proxy is checked in two steps:
        1. To see if proxy 'website' is available.

        In case of failiur, next proxy is tested with same procedure.
        This continues until working proxy is found.
        If no proxy is found, program exits.
        """
        count = 0
        for proxy in self.proxies:
            print("Trying %s" % (self.colorify("yellow", proxy)))
            self.logger.debug("Trying proxy: %s" % (proxy))
            self.soup = self.http_request(proxy)
            if self.soup.find('a')['href'] != proxy + "/full/" or self.soup == -1:
                print("Bad proxy!")
                count += 1
                if count == len(self.proxies):
                    self.logger.debug("Proxy list finished! Exiting!")
                    print("No more proxies found! Exiting...")
                    sys.exit(2)
            else:
                self.logger.debug("Connected to proxy...")
                print("Available!")
                self.proxy = proxy
                break

    def get_html(self):
        """
        To get HTML page.

        Once proxy is found, the HTML page for
        corresponding search string is fetched.
        Also, the time taken to fetch that page is returned.
        Uses http_request_time() from Common.py module.
        """
        for self.page in range(self.pages):
            print("\nFetching from page: %d" % (self.page+1))
            self.logger.debug("fetching page %d/%d" % (self.page, self.pages))
            search = "/usearch/%s/%d/" % (self.title, self.page + 1)
            self.soup, time = self.http_request_time(self.proxy + search)
            print("[in %.2f sec]" % (time))
            self.logger.debug("Page fetched in %.2f sec!" % (time))
            self.total_fetch_time += time
            self.soup_dict[self.page] = self.soup

    def parse_html(self):
        """
        Parse HTML to get required results.

        Results are fetched in masterlist list.
        Also, a mapper[] is used to map 'index'
        with torrent name, link and magnetic link
        """
        try:
            for page in self.soup_dict:
                self.soup = self.soup_dict[page]
                content = self.soup.find('table', class_='data')
                data = content.find_all('tr', class_='odd')
                for i in data:
                    name = i.find('a', class_='cellMainLink').string
                    if name is None:
                        name = i.find('a', class_='cellMainLink').get_text().split("[[")[0]
                    # Handling Unicode characters in windows.
                    torrent_link = i.find('a', class_='cellMainLink')['href']
                    uploader = i.find('span', class_='lightgrey').get_text().split(" ")[-4]
                    category = i.find('span', class_='lightgrey').get_text().split(" ")[-2]
                    verified_uploader = i.find('a', {'title': 'Verified Torrent'})
                    if verified_uploader is not None:
                        uploader = self.colorify("yellow", uploader)
                        comment_count = i.find('a', class_='icommentjs').get_text()
                    if comment_count == '':
                        comment_count = 0
                    misc_details = i.find_all('td', class_='center')
                    size = misc_details[0].string
                    date = misc_details[1].string
                    seeds = misc_details[2].string
                    leeches = misc_details[3].string
                    seeds_color = self.colorify("green", seeds)
                    leeches_color = self.colorify("red", leeches)
                    magnet = i.find('a', {'title': 'Torrent magnet link'})['href']
                    torrent_link = self.proxy+torrent_link
                    self.index += 1
                    self.mapper.insert(self.index, (name, magnet, torrent_link, self.class_name))
                    self.mylist = [category, name, '--' + str(self.index) +
                            '--', uploader, size, date, seeds_color+'/'+leeches_color, comment_count]
                    self.masterlist.append(self.mylist)
                    self.mylist_crossite = [name+" ({})".format(uploader), self.index, size, seeds+'/'+leeches, date]
                    self.masterlist_crossite.append(self.mylist_crossite)
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)


def main(title, page_limit):
    """Execution begins here."""
    try:
        print("\n[KickassTorrents]\n")
        print("Obtaining proxies...")
        kat = KickassTorrents(title, page_limit)
        kat.check_proxy()
        kat.get_html()
        kat.parse_html()
        kat.post_fetch()
        print("\nBye!")
    except KeyboardInterrupt:
        kat.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


def cross_site(title, page_limit):
    kat = KickassTorrents(title, page_limit)
    return kat


if __name__ == "__main__":
    print("Its a module!")
