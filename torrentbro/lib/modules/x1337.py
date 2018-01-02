"""1337x Module."""

import logging
import platform
import sys

from torrentbro.lib.utilities.Config import Config


class x1337(Config):
    """
    1337x class.

    This class fetches torrents from 1337x website,
    and diplays results in tabular form.
    Further, torrent's magnetic link,
    upstream link and files to be downloaded with torrent can be
    printed on console.
    Torrent can be added to client directly

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
        self.proxies = self.get_proxies('1337x')
        self.proxy = None
        self.title = title
        self.pages = page_limit
        self.logger = logging.getLogger('log1')
        self.class_name = self.__class__.__name__.lower()
        self.index = 0
        self.page = 0
        self.total_fetch_time = 0
        self.mapper = []
        self.mylist = []
        self.masterlist = []
        self.mylist_crossite = []
        self.masterlist_crossite = []
        self.soup_dict = {}
        self.headers = [
                'CATEG', 'NAME', 'INDEX', 'SE/LE', 'TIME', 'SIZE', 'UL', 'C']

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
        count = 1
        for proxy in self.proxies:
            print("Trying %s" % (self.colorify("yellow", proxy)))
            self.logger.debug("Trying proxy: %s" % (proxy))
            self.soup = self.http_request(proxy)
            try:
                if self.soup == -1 or "1337x" not in self.soup.head.title.string:
                    print("Bad proxy!")
                    count += 1
                    if count == len(self.proxies):
                        print("No more proxies found! Exiting...")
                        sys.exit(2)
                    else:
                        continue
                else:
                    print("Proxy available. Performing test...")
                    url = proxy+"/search/hello/1/"
                    self.logger.debug("Carrying out test for string 'hello'")
                    self.soup = self.http_request(url)
                    test = self.soup.find('table', class_='table-list')
                    if test is not None:
                        self.proxy = proxy
                        print("Pass!")
                        self.logger.debug("Test passed!")
                        break
                    else:
                        print("Test failed!\nPossibly site not reachable. (See logs)")
                        self.logger.debug("Test failed!")
            except (AttributeError, Exception) as e:
                print("Proxy not available\n")
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
                search = "/search/{}/{}/".format(self.title, self.page+1)
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
        with torrent name and link
        """
        try:
            for page in self.soup_dict:
                self.soup = self.soup_dict[page]
                content = self.soup.find('table', class_='table-list')
                if content is None:
                    return
                results = content.find_all('tr')
                for result in results[1:]:
                    content = result.findAll('td')
                    if len(content[0].findAll(text=True)) == 2:
                        name, comments = content[0].findAll(text=True)
                    else:
                        name = content[0].findAll(text=True)[0]
                        comments = 0
                    link = content[0].findAll('a')[1]['href']
                    link = self.proxy + link
                    category = content[0].a.i['class'][0].split('-')[1]
                    category = category.title()
                    seeds = content[1].string
                    leeches = content[2].string
                    seeds_color = self.colorify("green", seeds)
                    leeches_color = self.colorify("red", leeches)
                    date = content[3].string
                    size = content[4].findAll(text=True)[0]
                    uploader = content[5].string
                    uploader_status = content[5]['class'][1]
                    if uploader_status == 'vip':
                        name = self.colorify("cyan", name)
                        uploader = self.colorify("cyan", uploader)
                    self.index += 1
                    self.mapper.insert(self.index, (name, link, self.class_name))
                    self.mylist = [category, name, "--" +
                        str(self.index) + "--", seeds_color + '/' + leeches_color, date, size, uploader, comments]
                    self.masterlist.append(self.mylist)
                    self.mylist_crossite = [name+" ({})".format(uploader), self.index, size, seeds+'/'+leeches, date]
                    self.masterlist_crossite.append(self.mylist_crossite)
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" % (e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)


def main(title, page_limit):
    """Execution begins here."""
    try:
        print("\n[1337x]\n")
        print("Obtaining proxies...")
        x13 = x1337(title, page_limit)
        x13.check_proxy()
        x13.get_html()
        x13.parse_html()
        x13.post_fetch()
    except KeyboardInterrupt:
        x13.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


def cross_site(title, page_limit):
    x13 = x1337(title, page_limit)
    return x13
