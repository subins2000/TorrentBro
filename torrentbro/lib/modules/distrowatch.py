"""Modified for DistroWatch by Jesse Smith <jsmith@resonatingmedia.com>."""

import sys
import logging
from torrentbro.lib.utilities.Common import Common


class DistroWatch(Common):
    """
    Distrowatch class.

    This class fetches results from
    distrowatch.com and displays
    results in tabular form.
    Selected torrent is downloaded in hard-drive.
    Default download location is $HOME/downloads/torrench
    """

    def __init__(self, title):
        """Initialisations."""
        Common.__init__(self)
        self.title = title
        self.logger = logging.getLogger('log1')
        self.index = 0
        self.mylist = []
        self.masterlist = []
        self.urllist = []
        self.url = "https://distrowatch.com/dwres.php?resource=bittorrent"
        self.headers = ['NAME', 'INDEX', 'UPLOADED']
        self.mapper = []
        self.soup = None

    def fetch_results(self):
        """To fetch results for given input."""
        try:
            torrent = self.soup.find_all('td', 'torrent')
            torrent_date = self.soup.find_all('td', 'torrentdate')
            for i, j in zip(torrent, torrent_date):
                try:
                    link = i.find('a')
                    url = "https://distrowatch.com/" + link.get('href')
                    name = link.string
                    name = name.lower()
                    if self.title in name:
                        date = j.string
                        self.index += 1
                        self.mapper.insert(self.index, (name))
                        self.mylist = [name, "--" + str(self.index) + "--", date]
                        self.masterlist.append(self.mylist)
                        self.urllist.append(url)
                except AttributeError as e:
                    self.logger.exception(e)
                    pass
            if self.index == 0:
                print("No results found for give input!")
                self.logger.debug("\nNo results found for given input! Exiting!")
                sys.exit(2)
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)

    def select_torrent(self):
        """
        To select torrent and download.

        Torrent is selected thorugh index value.
        Selected torrent (.torrent file) is downloaded to hard-drive.
        Default download location is $HOME/downloads/torrench
        """
        self.logger.debug("Selecting torrent...")
        print("\nTorrent can be downloaded directly through index")
        temp = 9999
        while(temp != 0):
            try:
                temp = int(input("\n\n(0 = exit)\nindex > "))
                self.logger.debug("input index %d" % (temp))
                if temp == 0:
                    print("\nBye!")
                    self.logger.debug("Torrench quit!")
                    break
                elif temp < 0:
                    self.logger.debug("Invalid input index %d" % (temp))
                    print("\nBad Input\n")
                    continue
                else:
                    selected_torrent = self.mapper[temp-1]
                    self.logger.debug("selected torrent: %s ; index: %d" % (selected_torrent, temp))
                    selected_torrent = self.colorify("yellow", selected_torrent)
                    torrent_url = self.urllist[temp-1]
                    torrent_name = torrent_url.split('/')[5]
                    print("\nSelected index [%s] - %s" % (temp, selected_torrent))
                    load = 0
                    temp2 = input("\n1. Download Torrent and Load torrent to client [l]\n2. Download torrent ONLY [d]\n\nOption [l/d]: ")
                    if temp2 not in ['l', 'd']:
                        self.logger.debug("Inappropriate input! Should be [l/d] only!")
                        print("Bad input!\n")
                        continue
                    elif temp2 == 'l':
                        load = 1
                    else:
                        load = 0
                    self.download(torrent_url, torrent_name, load)
            except (ValueError, IndexError, KeyError, TypeError) as e:
                self.logger.exception(e)
                print("\nBad Input\n")


def main(title):
    """Execution begins here."""
    try:
        print("\n[DistroWatch]\n")
        title = title.lower()
        dw = DistroWatch(title)
        print("Fetching results...")
        dw.soup = dw.http_request(dw.url)
        dw.fetch_results()
        dw.logger.debug("Results fetched successfully!")
        dw.show_output()
        dw.select_torrent()
    except KeyboardInterrupt as e:
        dw.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


if __name__ == "__main__":
    print("Its a module!")
