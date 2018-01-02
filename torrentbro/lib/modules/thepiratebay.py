"""The Pirate Bay Module."""

import logging
import sys

from torrentbro.lib.utilities.Config import Config


class ThePirateBay(Config):
    """
    ThePirateBay class.

    This class fetches torrents from TPB proxy,
    and diplays results in tabular form.
    Further, torrent details can be fetched which are
    stored in dynamically-generated HTML page.
    Details are fetched from tpb_details module
    and stored in $HOME/.torrench/temp directory.

    All activities are logged and stored in a log file.
    In case of errors/unexpected output, refer logs.
    """

    def __init__(self, title, page_limit):
        """Initialisations."""
        Config.__init__(self)
        self.proxies = self.get_proxies('tpb')
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
        self.headers = [
                'CATEG', 'NAME', 'INDEX', 'UPLOADER', 'SIZE', 'SE/LE', 'DATE', 'C']
        ###################################
        self.non_color_name = None
        self.top = "/top/all"
        self.top48 = "/top/48hall"

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
                if self.soup == -1 or self.soup.a.string != 'The Pirate Bay':
                    print("Bad proxy!")
                    count += 1
                    if count == len(self.proxies):
                        print("No more proxies found! Exiting...")
                        sys.exit(2)
                    else:
                        continue
                else:
                    print("Proxy available. Performing test...")
                    url = proxy+"/search/hello/0/99/0"
                    self.logger.debug("Carrying out test for string 'hello'")
                    self.soup = self.http_request(url)
                    test = self.soup.find('div', class_='detName')
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
                search = "/search/%s/%d/99/0" % (self.title, self.page)
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

    def get_top_html(self):
        """To get top torrents."""
        try:
            print(self.colorify("green", "\n\n*Top 100 TPB Torrents*"))
            print("1. Top (ALL)\n2. Top (48H)\n")
            option = int(input("Option: "))
            if option == 1:
                self.logger.debug("Selected [TOP-ALL] (Option: %d)" % (option))
                self.soup, time = self.http_request_time(self.proxy + self.top)
            elif option == 2:
                self.logger.debug("Selected [TOP-48h] (Option: %d)" % (option))
                self.soup, time = self.http_request_time(self.proxy + self.top48)
            else:
                print("Bad Input! Exiting!")
                sys.exit(2)
            self.total_fetch_time = time
            self.soup_dict[0] = self.soup
        except ValueError as e:
            print("Bad input! Exiting!")
            self.logger.exception(e)
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
                content = self.soup.find('table', id="searchResult")
                if content is None:
                    return
                data = content.find_all('tr')
                for i in data[1:]:
                    name = i.find('a', class_='detLink').string
                    uploader = i.find('font', class_="detDesc").a
                    if name is None:
                        name = i.find('a', class_='detLink')['title'].split(" ")[2:]
                        name = " ".join(str(x) for x in name)
                    if uploader is None:
                        uploader = i.find('font', class_="detDesc").i.string
                    else:
                        uploader = uploader.string
                    comments = i.find(
                        'img', {'src': '//%s/static/img/icon_comment.gif' % (self.proxy.split('/')[2])})
                    # Total number of comments
                    if comments is None:
                        comment = '0'
                    else:
                        comment = comments['alt'].split(" ")[-2]
                    # See if uploader is VIP/Truested/Normal Uploader
                    self.non_color_name = name
                    is_vip = i.find('img', {'title': "VIP"})
                    is_trusted = i.find('img', {'title': 'Trusted'})
                    if(is_vip is not None):
                        name = self.colorify("green", name)
                        uploader = self.colorify("green", uploader)
                    elif(is_trusted is not None):
                        name = self.colorify("magenta", name)
                        uploader = self.colorify("magenta", uploader)
                    categ = i.find('td', class_="vertTh").find_all('a')[0].string
                    sub_categ = i.find('td', class_="vertTh").find_all('a')[1].string
                    seeds = i.find_all('td', align="right")[0].string
                    leeches = i.find_all('td', align="right")[1].string
                    date = i.find('font', class_="detDesc").get_text().split(' ')[1].replace(',', "")
                    size = i.find('font', class_="detDesc").get_text().split(' ')[3].replace(',', "")
                    seeds_color = self.colorify("green", seeds)
                    leeches_color = self.colorify("red", leeches)
                    # Unique torrent id
                    torr_id = i.find('a', {'class': 'detLink'})["href"].split('/')[2]
                    # Upstream torrent link
                    link = "%s/torrent/%s" % (self.proxy, torr_id)
                    magnet = i.find_all('a', {'title': 'Download this torrent using magnet'})[0]['href']
                    self.index += 1
                    self.mapper.insert(self.index, (name, magnet, link, self.class_name))
                    self.mylist = [categ + " > " + sub_categ, name, "--" +
                                str(self.index) + "--", uploader, size, (seeds_color + '/' +
                                leeches_color), date, comment]
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
        print("\n[The Pirate Bay]\n")
        print("Obtaining proxies...")
        tpb = ThePirateBay(title, page_limit)
        tpb.check_proxy()
        if title is None:
            tpb.get_top_html()
        else:
            tpb.get_html()
        tpb.parse_html()
        tpb.post_fetch()
        print("\nBye!")
    except KeyboardInterrupt:
        tpb.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


def cross_site(title, page_limit):
    tpb = ThePirateBay(title, page_limit)
    return tpb


if __name__ == "__main__":
    print("It's a module!")
