import logging
import logging.handlers
import os
import sys

from repoman_client.config import config
from repoman_client.exceptions import RepomanError, LoggingError

# This class is to be used for all logging in the repoman client.
# You should not need to instantiate it; a global singleton instance
# of it will be accessible when you include this module into your
# own modules.
class Logger(object):

    _instance = None

    @staticmethod
    def get_instance():
        if Logger._instance == None:
            Logger._instance = Logger()
        return Logger._instance

    logger = None
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    log_filename = None
    def __init__(self):
        self.log_filename = None
        self.logger = logging.getLogger('repoman')
        self.logger.setLevel(logging.INFO)

        if config.logging_enabled:
            logging_dir = config.logging_dir
            if logging_dir == '':
                # nothing to do in the case of empty logging_dir
                pass
            elif os.path.exists(logging_dir) and not os.path.isdir(logging_dir):
                raise LoggingError('The logging directory path specified in the configuration file (and listed below) already exists and is not a directory.\n\n[%s]\n\n  Please chose a different logging directory.' % (logging_dir))
            elif not os.path.exists(logging_dir):
                try:
                    os.makedirs(logging_dir)
                    uid = os.environ.get('SUDO_UID', os.getuid())
                    gid = os.environ.get('SUDO_GID', os.getgid())
                    os.chown(logging_dir, int(uid), int(gid))
                except Exception, e:
                    raise LoggingError("Error: Logging dir '%s' does not exist and I am unable to create it.\n%s" % (logging_dir, e))
            
            self.log_filename = os.path.join(config.logging_dir, "repoman-client.log")
            fh = logging.handlers.TimedRotatingFileHandler(self.log_filename, when="midnight", backupCount=10)
            self.logger.setLevel(config.logging_level)
            fh.setLevel(config.logging_level)
            fh.setFormatter(self.formatter)
            self.logger.addHandler(fh)
            self.logger.debug('Logger initialized.  Logging to %s, level %d' % (self.log_filename, config.logging_level))
        else:
            self.logger.addHandler(logging.NullHandler())



    def get_logger(self):
        return self.logger

    def is_enabled(self):
        return config.logging_enabled

    def get_log_filename(self):
        return self.log_filename

    def enable_debug(self):
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
            

# Globally accessible logger singleton
repoman_logger = None
log = None
try:
    repoman_logger = Logger.get_instance()
    log = repoman_logger.get_logger()
except RepomanError, e:
    print e
    sys.exit(1)
