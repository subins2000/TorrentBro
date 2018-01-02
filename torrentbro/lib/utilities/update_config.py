"""config.ini file update module"""

from torrentbro.lib.utilities.Config import Config
import logging


class ConfigUpdate(Config):
    """
    ConfigUpdate class

    config.ini file can be updated only if it is already present
    and enabled by the user.
    """
    def __init__(self):
        Config.__init__(self)
        self.logger = logging.getLogger('log1')

    def start_update(self):
        # If config.ini file is not present or not enabled, terminate.
        if not self.file_exists():
            error = "[Error] Config file is either not present or not enabled. Terminating.\n"
            error = self.colorify("red", error)
            self.logger.debug("Config file not present. Unable to update file.")
            print(error)
        else:
            # config.ini file is present and enabled. Continue updating.
            self.logger.debug("Config file present. Updating config file.")
            self.update_file()  # Defined in Config.py


def main():
    """Execution begins here"""
    c = ConfigUpdate()
    c.start_update()


if __name__ == "__main__":
    print("It's a module.")
