"""
Logger Module.

This module defines logging setting to use.
"""
import platform
import os

if platform.system() == "Windows":
    log_home = os.path.expanduser(os.path.join(os.path.join('~', 'AppData'), 'Local'))
else:
    log_home = os.getenv('XDG_DATA_HOME', os.path.expanduser(os.path.join(os.path.join('~', '.local'), 'share')))

log_directory = os.path.join(log_home, 'torrench')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
logfile_name = os.path.join(log_directory, "torrentbro.lib.log")

LOG_SETTINGS = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': "%(asctime)s: (%(filename)s->%(funcName)s #%(lineno)d): [%(levelname)s] - %(message)s"
            }
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': logfile_name,
                'when': 'midnight',
                'interval': 1,
                'backupCount': 5
            }
        },
        'loggers': {
            'log1': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }
