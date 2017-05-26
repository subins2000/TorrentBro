#!/usr/bin/python3

import os
import sys

from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
from PyQt5.QtWidgets import QApplication, QWidget

from Home import *

baseDir = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    qtTranslator = QTranslator()
    qtTranslator.load('torrentbro_' + QLocale.system().name(), QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qtTranslator)

    ex = Home(baseDir)
    sys.exit(app.exec_())
