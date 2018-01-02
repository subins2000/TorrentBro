"""The Pirate Bay Module."""

import logging
import sys

from torrentbro.lib.utilities.Config import Config


class LimeTorrents(Config):
    """
    LimeTorrents class.

    This class fetches torrents from LimeTorrents proxy,
    and diplays results in tabular form.

    All activities are logged and stored in a log file.
    In case of errors/unexpected output, refer logs.
    """

    def __init__(self, title, page_limit):
        """Initialisations."""
        Config.__init__(self)
        self.proxies = self.get_proxies('limetorrents')
        self.proxy = None
        self.title = title
        self.pages = page_limit
        self.logger = logging.getLogger('log1')
        self.class_name = self.__class__.__name__.lower()
        self.index = 0
        self.page = 0
        self.total_fetch_time = 0
        self.mylist = []
        self.masterlist = []
        self.mylist_crossite = []
        self.masterlist_crossite = []
        self.mapper = []
        self.soup_dict = {}
        self.soup = None
        self.headers = ['NAME', 'INDEX', 'SIZE', 'SE/LE', 'UPLOADED']

    def check_proxy(self):
        """
        To check proxy availability.

        Proxy is checked in two steps:
        1. To see if proxy 'website' is available.
        2. A test is carried out with a sample string 'hello'.
        If results are found, test is passed, else test failed!

        This class inherits Config class. Config class inherits
        Common class. The Config class provides proxies list fetched
        from config file. The Common class consists of commonly used
        methods.

        In case of failiur, next proxy is tested with same procedure.
        This continues until working proxy is found.
        If no proxy is found, program exits.
        """
        count = 0
        for proxy in self.proxies:
            print("Trying %s" % (self.colorify("yellow", proxy)))
            self.logger.debug("Trying proxy: %s" % (proxy))
            self.soup = self.http_request(proxy)
            try:
                if self.soup == -1 or 'limetorrents' not in self.soup.find('div', id='logo').a['title'].lower():
                    print("Bad proxy!\n")
                    count += 1
                    if count == len(self.proxies):
                        print("No more proxies found! Terminating")
                        sys.exit(2)
                    else:
                        continue
                else:
                    print("Proxy available. Performing test...")
                    url = proxy+"/search/all/hello/seeds/1/"
                    self.logger.debug("Carrying out test for string 'hello'")
                    self.soup = self.http_request(url)
                    test = self.soup.find('table', class_='table2')
                    if test is not None:
                        self.proxy = proxy
                        print("Pass!")
                        self.logger.debug("Test passed!")
                        break
                    else:
                        print("Test failed!\nPossibly site not reachable. See logs.")
                        self.logger.debug("Test failed!")
            except (AttributeError, Exception) as e:
                self.logger.exception(e)
                pass

    def get_html(self):
        """
        To get HTML page.

        Once proxy is found, the HTML page for
        corresponding search string is fetched.
        Also, the time taken to fetch that page is returned.
        Uses http_request_time() from Common.py module.
        """
        try:
            for self.page in range(self.pages):
                print("\nFetching from page: %d" % (self.page+1))
                search = "/search/all/{}/seeds/{}/".format(self.title, self.page+1)
                self.soup, time = self.http_request_time(self.proxy + search)
                self.logger.debug("fetching page %d/%d" % (self.page+1, self.pages))
                print("[in %.2f sec]" % (time))
                self.logger.debug("page fetched in %.2f sec!" % (time))
                self.total_fetch_time += time
                self.soup_dict[self.page] = self.soup
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)

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
                content = self.soup.find('table', class_='table2')
                if content is None:
                    return
                results = content.findAll('tr')
                for result in results[1:]:
                    data = result.findAll('td')
                    # try block is limetorrents-specific. Means only limetorrents requires this.
                    try:
                        name = data[0].findAll('a')[1].string
                        link = data[0].findAll('a')[1]['href']
                        link = self.proxy+link
                        date = data[1].string
                        date = date.split('-')[0]
                        size = data[2].string
                        seeds = data[3].string.replace(',', '')
                        leeches = data[4].string.replace(',', '')
                        seeds_color = self.colorify("green", seeds)
                        leeches_color = self.colorify("red", leeches)
                        self.index += 1
                        self.mapper.insert(self.index, (name, link, self.class_name))
                        self.mylist = [name, "--" +
                                    str(self.index) + "--", size, seeds_color+'/'+
                                    leeches_color, date]
                        self.masterlist.append(self.mylist)
                        self.mylist_crossite = [name, self.index, size, seeds+'/'+leeches, date]
                        self.masterlist_crossite.append(self.mylist_crossite)
                    except Exception as e:
                        self.logger.exception(e)
                        pass
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" % (e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)


def main(title, page_limit):
    """Execution begins here."""
    try:
        print("\n[LimeTorrents]\n")
        print("Obtaining proxies...")
        lmt = LimeTorrents(title, page_limit)
        lmt.check_proxy()
        lmt.get_html()
        lmt.parse_html()
        lmt.post_fetch()  # defined in Common.py
        print("\nBye!")
    except KeyboardInterrupt:
        lmt.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


def cross_site(title, page_limit):
    lmt = LimeTorrents(title, page_limit)
    return lmt


if __name__ == "__main__":
    print("It's a module!")
