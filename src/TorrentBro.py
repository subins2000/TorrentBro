#!/usr/bin/python3

import sys

from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
from PyQt5.QtWidgets import QApplication, QWidget

from Home import *

if __name__ == '__main__':
    app = QApplication(sys.argv)

    qtTranslator = QTranslator()
    qtTranslator.load('torrentbro_' + QLocale.system().name(),
                      QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qtTranslator)

    ex = Home()
    sys.exit(app.exec_())
