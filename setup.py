#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name='TorrentBro',
    version='0.2.1',
    url='https://github.com/subins2000/torrentbro',
    author='Subin Siby',
    author_email='subins2000@gmail.com',
    description=('A torrent browser.'),
    license='GPL',
    install_requires=[
        'purl',
        'python-dateutil',
        'lxml',
        'cssselect',
        'requests',
        'pyqt5'
    ],
    packages=find_packages(exclude=['designer']),
    entry_points={'gui_scripts': [
        'torrentbro = torrentbro.TorrentBro:main'
    ]},
)
