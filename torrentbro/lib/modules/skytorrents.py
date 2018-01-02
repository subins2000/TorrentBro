"""SkyTorrents Module."""

import logging
import sys

from torrentbro.lib.utilities.Config import Config


class SkyTorrents(Config):
    """
    SkyTorrents class.

    This class fetches torrents from SKY website,
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
        self.proxies = self.get_proxies('sky')
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
        self.soup = None
        self.headers = ["NAME  ["+self.colorify("green", "+UPVOTES")+"/"+self.colorify("red", "-DOWNVOTES")+"]",
                               "INDEX", "SIZE", "date", "SE/LE"]
        ######################################
        self.top = "/top1000/all/ed/%d/?l=en-us" % (self.page)

    def check_proxy(self):
        """
        To check proxy (site) availability.

        Though skytorrents (as of now) is only using the
        main site, the function is named as check_proxy to
        confirm uniformity across modules.
        In case of failiur, program exits.
        """
        try:
            count = 0
            for proxy in self.proxies:
                print("Trying %s" % (self.colorify("yellow", proxy)))
                self.logger.debug("Trying proxy: %s" % (proxy))
                """
                Performing test for string hello.
                """
                self.logger.debug("Carrying out test for string 'hello'")
                self.soup = self.http_request(proxy + "/search/all/ed/1/?l=en-us&q=hello")
                if self.soup.find_all('tr')[1] is None or self.soup is None or self.soup == -1:
                    print("Bad proxy!")
                    count += 1
                    if count == len(self.proxies):
                        self.logger.debug("Proxy list finished! Exiting!")
                        print("No more proxies found! Exiting...")
                        sys.exit(2)
                else:
                    self.logger.debug("Passed! Connected to proxy!")
                    print("Available!")
                    self.proxy = proxy
                    break
        except Exception as e:
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            self.logger.exception(e)
            sys.exit(2)

    def get_top_html(self):
        """To get top 1000 torrents."""
        print(self.colorify("green", "\n\n*Top 1000 SkyTorrents*"))
        print("1000 Torrents are divided into 25 pages (1 page = 40 torrents)\n")
        try:
            option = int(input("Enter number of pages (0<n<=25): "))
            if option <= 0 or option >= 25:
                print("Bad input! Exiting!")
                sys.exit(2)
            else:
                self.pages = option
        except ValueError as e:
            print("Bad input! Exiting!")
            self.logger.exception(e)
            sys.exit(2)

    def get_html(self):
        """
        To get HTML page.

        Once proxy is found, the HTML page for
        corresponding search string is fetched.
        Also, the time taken to fetch that page is returned.
        Uses http_request_time() from Common.py module.

        Also, TOP torrents search is resolved here.
        The variable [search] is set accordingly.
        If --top is used, title is set to None. This is the condition
        checked for --top.
        """
        try:
            for self.page in range(self.pages):
                print("\nFetching from page: %d" % (self.page+1))
                self.logger.debug("fetching page %d/%d" % (self.page+1, self.pages))
                """
                If title is none, get TOP torrents.
                """
                if self.title is None:
                    search = "/top1000/all/ed/%d/?l=en-us" % (self.page+1)
                else:
                    search = "/search/all/ed/%d/?l=en-us&q=%s" % (self.page+1, self.title)
                self.soup, time = self.http_request_time(self.proxy + search)
                print("[in %.2f sec]" % (time))
                self.logger.debug("page fetched in %.2f sec!" % (time))
                self.total_fetch_time += time
                self.soup_dict[self.page] = self.soup
        except Exception as e:
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            self.logger.exception(e)
            sys.exit(2)

    def parse_html(self):
        """
        Parse HTML to get required results.

        Results are fetched in masterlist list.
        Also, a mapper[] is used to map 'index'
        with torrent name, link and magnetic link
        and files_count (counts number of files torrent has)
        """
        try:
            for page in self.soup_dict:
                self.soup = self.soup_dict[page]
                content = self.soup.find_all("tr")
                for i in range(len(content)):
                    if i == 0:
                        continue
                    data = content[i]
                    results = data.find_all("td")
                    name = results[0].find_all('a')[0].string
                    upvotes = '0'
                    downvotes = '0'
                    try:
                        upvotes = str(results[0]).split("\xa0")[1].replace(" ", "").split("<")[0]
                    except IndexError as e:
                        self.logger.exception(e)
                        pass
                    try:
                        downvotes = str(results[0]).split("\xa0")[2].replace(" ", "").split("<")[0]
                    except IndexError as e:
                        self.logger.exception(e)
                        pass
                    upvotes = self.colorify("green", ("+"+upvotes))
                    downvotes = self.colorify("red", ("-"+downvotes))
                    display_votes = "  [%s]" % (upvotes+"/"+downvotes)
                    link = results[0].find_all('a')[0]['href']
                    magnet = results[0].find_all('a')[1]['href']
                    size = results[1].string
                    #self.file_count = results[2].string
                    date = results[3].string
                    seeds = results[4].string
                    leeches = results[5].string
                    seeds_color = self.colorify("green", seeds)
                    leeches_color = self.colorify("red", leeches)
                    self.index += 1
                    self.mapper.insert(self.index, (name, magnet, self.proxy+link, self.class_name))
                    #self.mylist = [name + "["+str(upvotes)+"/"+str(downvotes)+"]", "--"+str(self.index)+"--", size, date, seeds, leeches]
                    self.mylist = [name + display_votes,
                            "--"+str(self.index)+"--", size,
                            date, (seeds_color + '/' + leeches_color)]
                    self.masterlist.append(self.mylist)
                    # Lists used for cross-site
                    self.mylist_crossite = [name+display_votes, self.index, size, seeds+'/'+leeches, date]
                    self.masterlist_crossite.append(self.mylist_crossite)
        except Exception as e:
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            self.logger.exception(e)
            sys.exit(2)


def main(title, page_limit):
    """Execution begins here."""
    try:
        print("\n[SkyTorrents]\n")
        print("Obtaining proxies...")
        sky = SkyTorrents(title, page_limit)
        sky.check_proxy()
        if title is None:
            sky.get_top_html()
        sky.get_html()
        sky.parse_html()
        sky.post_fetch()
    except KeyboardInterrupt:
        sky.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


def cross_site(title, page_limit):
    sky = SkyTorrents(title, page_limit)
    return sky


if __name__ == "__main__":
    print("Its a module!")
