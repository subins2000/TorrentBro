"""LibGen Module."""

import logging
import sys
import time

import requests
from torrentbro.lib.utilities.Config import Config


class LibGen(Config):
    """
    LibGen Class.

    Torrench uses LibGen API instead of scrapping the web.
    """
    def __init__(self, isbn):
        """Initialisations."""
        Config.__init__(self)
        self.proxies = self.get_proxies('libgen')
        self.proxy = self.proxies[0]
        self.logger = logging.getLogger('log1')
        self.isbn = isbn
        self.index = 0
        self.mapper = []
        self.mapper2 = []
        self.total_fetch_time = 0
        self.output_headers = [
                'Author(s)',
                'Title',
                'INDEX',
                'Publisher',
                'Year',
                'Language',
                ]

    def search_torrent(self):
        """To search torrent for given input.

        The API gives out results in JSON format.
        """
        try:
            masterlist = []
            fields = ('Author,Title,Year,Edition,Pages,Publisher,Extension,Language,MD5,FileSize,descr')
            params = "json.php?isbn={}&fields={}".format(self.isbn, fields)
            self.logger.debug("Fetching results")
            start_time = time.time()
            results = requests.get(self.proxy+params).json()
            self.total_fetch_time = time.time() - start_time
            if results == []:
                print("No results found for given input!")
                print("\nNote: LibGen (for now) supports searching for Ebooks using book's ISBN-10 number ONLY.")
                print("Please refer docs for more information about the same.")
                self.logger.debug("No results found!")
                self.logger.debug("Exiting!")
                sys.exit(2)
            for result in results:
                title = result['title']
                author = result['author']
                edition = result['edition']
                pages = result['pages']
                extension = result['extension'].upper()
                publisher = result['publisher']
                language = result['language']
                year = result['year']
                md5 = result['md5']
                size = float(result['filesize'])
                size = "{:.2f} MB".format(size/1000000)
                descr = result['descr']
                self.index += 1
                self.mapper2.insert(self.index, (title, author, edition, pages, publisher, extension, language, year, md5, size, descr))
                #################################################################
                size = self.colorify("green", " ({}) ".format(size))
                extension = self.colorify("yellow", "({})".format(extension))
                self.mapper.insert(self.index, (title+size+extension, md5))
                self.mylist = [author, title+size+extension, "--" +
                    str(self.index) + "--", publisher, year, language]
                masterlist.append(self.mylist)
            self.logger.debug("Results fetched successfully!")
            self.show_output(masterlist, self.output_headers)
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" % (e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)

    def after_output_text(self):
        """
        After output is displayed, Following text is displayed on console.

        Text includes instructions, total torrents fetched, total pages,
        and total time taken to fetch results.
        """
        oplist = [self.index, self.total_fetch_time]
        self.after_output('libgen', oplist)

    def select_torrent(self):
        """
        To select required torrent.

        Torrent is selected through index value.
        Three options are present:
        1. To print Ebook details
        2. Load torrent to client
        3. Download .torrent file ONLY
        """
        self.logger.debug("Selecting torrent...")
        temp = 9999
        while(temp != 0):
            try:
                temp = int(input("\n(0=exit)\nindex > "))
                self.logger.debug("selected index %d" % (temp))
                if temp == 0:
                    print("\nBye!")
                    self.logger.debug("Torrench quit!")
                    break
                elif temp < 0:
                    print("\nBad Input!")
                    continue
                else:
                    selected_torrent, torrent_md5 = self.mapper[temp-1]
                    self.logger.debug("selected torrent: %s ; index: %d" % (selected_torrent, temp))
                    print("Selected index [%d] - %s\n" % (temp, self.colorify("yellow", selected_torrent)))
                    temp2 = input("1. Print Details [p]\n2. Load torrent to client [l]\n3. Download torrent ONLY [d]\n\nOption [p/l/d]: ")
                    temp2 = temp2.lower()
                    self.logger.debug("selected option: [%c]" % (temp2))
                    load = 0
                    if temp2 not in ['p', 'l', 'd']:
                        self.logger.debug("Inappropriate input! Should be [l/d] only!")
                        print("Bad input!")
                        continue
                    elif temp2 == 'p':
                        self.logger.debug("printing details")
                        self.print_info(self.mapper2[temp-1])
                    else:
                        if temp2 == 'l':
                            load = 1
                        try:
                            self.logger.debug("Loading magnetic link to client")
                            dload_link = "book/index.php?md5={}&oftorrent=".format(torrent_md5)
                            dload_link = self.proxy + dload_link
                            self.download(dload_link, torrent_md5+".torrent", load)
                        except Exception as e:
                            self.logger.exception(e)
                            continue
            except (ValueError, IndexError, TypeError) as e:
                print("\nBad Input!")
                self.logger.exception(e)
                continue

    def print_info(self, details):
        """
        To print Ebook details.

        Details include: title, author, edition, pages, publisher, extension, language, year, md5, size, descrption.
        """
        title, author, edition, pages, publisher, extension, language, year, md5, size, descr = details
        print("\n Title: {}\n".format(title),
              "Author: {}\n".format(author),
              "Edition: {}\n".format(edition),
              "Pages: {}\n".format(pages),
              "Publisher: {}\n".format(publisher),
              "Language: {}\n".format(language),
              "Year: {}\n".format(year),
              "Extension: {}\n".format(extension),
              "Size: {}\n".format(size),
              "MD5: {}\n\n".format(md5),
              "Description: {}".format(descr)
              )


def main(isbn):
    """Execution begins here."""
    print("\n[LibGen]\n")
    lgn = LibGen(isbn)
    lgn.search_torrent()
    lgn.after_output_text()
    lgn.select_torrent()


if __name__ == "__main__":
    print("It's a module.")
