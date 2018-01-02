""" Config module."""
import logging
import os
from configparser import SafeConfigParser

from torrentbro.lib.utilities.Common import Common


class Config(Common):
    r"""
    Config class.

    This class checks for config file's presence.
    Also, this class manages TPB/KAT proxies; That is,
    obtains TPB/KAT URL and fetches proxies thorugh those URL.
    Proxies are stored as list and returned.

    By default, Config files is checked in $XDG_CONFIG_HOME/torrench/ and
    fallback to $HOME/.config/torrench/ directory (linux)
    For windows, default location is ~\.config\torrench

    This class inherits Common class.
    """

    def __init__(self):
        """Initialisations."""
        Common.__init__(self)
        self.config = SafeConfigParser()
        self.config_dir = os.getenv('XDG_CONFIG_HOME', os.path.expanduser(os.path.join('~', '.config')))
        self.full_config_dir = os.path.join(self.config_dir, 'torrench')
        self.config_file_name = "config.ini"
        self.config_file_name_new = "config.ini.new"
        self.config_file = os.path.join(self.full_config_dir, self.config_file_name)
        self.config_file_new = os.path.join(self.full_config_dir, self.config_file_name_new)
        self.url = None
        self.name = None
        self.urllist = []
        self.logger = logging.getLogger('log1')

    def file_exists(self):
        """To check whether config.ini file exists and is enabled or not."""
        if os.path.isfile(self.config_file):
            self.config.read(self.config_file)
            enable = self.config.get('Torrench-Config', 'enable')
            if enable == '1':
                self.logger.debug("Config file exists and enabled!")
                return True

    def update_file(self):
        try:
            # Get updated copy of config.ini file.
            self.logger.debug("Downloading new config.ini file")
            url = "https://pastebin.com/raw/reymRHSL"
            self.logger.debug("Download complete. Saving file..")
            soup = self.http_request(url)
            res = soup.p.get_text()
            with open(self.config_file, 'w', encoding="utf-8") as f:
                f.write(res)
                self.logger.debug("Saved new file as {}".format(self.config_file))
            # Read file and set enable = 1
            self.config.read(self.config_file)
            self.logger.debug("Now enabling file")
            self.config.set('Torrench-Config', 'enable', '1')
            # Write changes to config.ini file (self.config_file)
            with open(self.config_file, 'w', encoding="utf-8") as configfile:
                self.config.write(configfile)
                self.logger.debug("File enabled successfull and saved.")
            print("Config file updated!")
            self.logger.debug("Config file updated successfully.")
        except Exception as e:
            print("Something went wrong. See logs for details.")
            self.logger.debug("Something gone wrong while updating config file.")
            self.logger.exception(e)

    # To get proxies for KAT/TPB/...
    def get_proxies(self, name):
        """
        Get Proxies.

        Proxies are read from config.ini file.
        """
        self.logger.debug("getting proxies for '%s'" % (name))
        temp = []
        self.config.read(self.config_file)

        name = '{}_URL'.format(name.upper())

        self.url = self.config.get('Torrench-Config', name)
        self.urllist = self.url.split()

        if name == 'TPB_URL':
            soup = self.http_request(self.urllist[-1])
            link = soup.find_all('td', class_='site')
            del self.urllist[-1]
            for i in link:
                temp.append(i.a["href"])
            self.urllist.extend(temp)
        elif name == "1337X_URL":
            soup = self.http_request(self.urllist[-1])
            link = soup.findAll('td', class_='text-left')
            del self.urllist[-1]
            for i in link:
                temp.append(i.a["href"])
            self.urllist.extend(temp)
        self.logger.debug("got %d proxies!" % (len(self.urllist)))
        return self.urllist
