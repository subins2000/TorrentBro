
import logging
import platform
from sys import exit as _exit

import torrentbro.lib.modules.distrowatch as distrowatch
import torrentbro.lib.modules.idope as idope
import torrentbro.lib.modules.kickasstorrent as kat
import torrentbro.lib.modules.libgen as libgen
import torrentbro.lib.modules.linuxtracker as linuxtracker
import torrentbro.lib.modules.nyaa as nyaa_module
import torrentbro.lib.modules.rarbg as rarbg
import torrentbro.lib.modules.skytorrents as sky
import torrentbro.lib.modules.thepiratebay as tpb_module
import torrentbro.lib.modules.x1337 as x13
import torrentbro.lib.modules.xbit as xbit_module
from torrentbro.lib.utilities.Config import Config


class InteractiveMode:
    """
    This class deals with most of the functionality assigned to the interactive mode.
    It resolves the arguments, parses and calls their respective modules
    :params: None
    """
    def __init__(self):
        self._modules = {}
        self.logger = logging.getLogger('log1')
        self.OS_WIN = False
        if platform.system() == "Windows":
            self.OS_WIN = True

    def parser(self, query):
        """
        :query: String to query the module.
        """
        _available_modules = self._set_modules().keys()
        if query[:4] in ('!h', 'help'):
            self.logger.debug("Display !h (help menu)")
            self._interactive_help()
        elif query[:2] in _available_modules:
            self._caller(query[:2], query[3:])
        elif query[:4] in ('!q', 'quit'):
            self.logger.debug("!q selected. Exiting interactive mode")
            print("Bye!")
            _exit(2)
        else:
            if query[:2] in self._extra_modules:
                print('Unbound command, please see https://github.com/kryptxy/torrench#-sites-hosting-illegal-content-must-read')
                print('Try `!h` or `help` for help.')
            else:
                self.logger.debug("Invalid command input")
                print('Invalid command! Try `!h` or `help` for help.')

    def _set_modules(self):
        """
        Map functions to commands and return dictionary.
        """
        self._default_modules = {
            '!d': distrowatch,
            '!l': linuxtracker
        }
        self._extra_modules = {
            '!t': tpb_module,
            '!n': nyaa_module,
            '!k': kat,
            '!b': xbit_module,
            '!s': sky,
            '!r': rarbg,
            '!i': idope,
            '!x': x13,
            '!g': libgen
        }

        if Config().file_exists():
            self._modules = self._default_modules.copy()
            self._modules.update(self._extra_modules)
        else:
            self.logger.debug("Config file not setup!")
            self._modules = self._default_modules

        return self._modules

    def _caller(self, module, query):
        """
        Send queries to their respective modules.

        :module: Module to use in query.
        :query: String to search for.
        """
        _modules = self._set_modules()
        if query and module in _modules and not query.isspace():
            self.logger.debug("Selected module %s, query: %s" % ((module), query))
            if module in ['!t', '!k', '!s', '!i', '!x', '!n']:
                _modules[module].main(query, page_limit=1)
            else:
                _modules[module].main(query)
        else:
            print("You called an invalid module or provided an empty query.")
            self.logger.debug("Called an invalid module or provided an empty query.")

    @staticmethod
    def _interactive_help():
        """
        Display help
        """
        help_text = """
            Available commands:
        !h or help  - Help text (this)
        !q or quit  - Quit interactive mode
        !l <string> - Search on LinuxTorrents
        !d <string> - Search on DistroWatch

        =========== Requires Config file ==========
        !n <string> - Search on nyaa.si for anime.
        !t <string> - Search on ThePirateBay.
        !k <string> - Search on KickAssTorrents.
        !r <string> - Search on RarBg
        !x <string> - Search on 1337x
        !s <string> - Search on SkyTorrents
        !b <string> - Search on xBit.pw
        !g <string> - Search on LibGen (Ebooks)
        ===========================================
        These commands are only available after a `config.ini` file has been set.
        See the documentation for more information.
        """
        print(help_text)


def inter():
    """
    Execution will start here.
    """
    try:
        i = InteractiveMode()
        while True:
            if not i.OS_WIN:
                data = input(Config().colorify("yellow", '\ntorrench > '))
            else:
                data = input('\ntorrench > ')
            i.logger.debug(data)
            data = data.replace("'", "")
            i.parser(data)
    except (KeyboardInterrupt, EOFError):
        print('Terminated.')
        i.logger.debug("Terminated.")


if __name__ == '__main__':
    print("Run torrench -i")
