import logging
import logging.handlers
import os
import sys

from repoman_client.config import config

# This class is to be used for all logging in the repoman client.
# You should not need to instantiate it; a global singleton instance
# of it will be accessible when you include this module into your
# own modules.
class Logger():
    logger = None

    def __init__(self):
        log_filename = None
        if config.logging_enabled:
            logging_dir = config.logging_dir
            if not os.path.isdir(logging_dir):
                try:
                    os.makedirs(logging_dir)
                    uid = os.environ.get('SUDO_UID', os.getuid())
                    gid = os.environ.get('SUDO_GID', os.getgid())
                    os.chown(logging_dir, int(uid), int(gid))
                except Exception as e:
                    print "Error: Logging dir '%s' does not exist and I am unable to create it.\n%s" % (logging_dir, e)
                    sys.exit(1)
            
            log_filename = os.path.join(config.logging_dir, "repoman-client.log")
        else:
            log_filename = '/dev/null'

        self.logger = logging.getLogger('repoman')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

        fh = logging.handlers.TimedRotatingFileHandler(log_filename, when="midnight", backupCount=10)
        fh.setLevel(config.logging_level)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.debug('Logger initialized.  Logging to %s, level %d' % (log_filename, config.logging_level))

    def get_logger(self):
        return self.logger

    def enable_debug(self):
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
            

# Globally accessible logger singleton
repoman_logger = Logger()
log = repoman_logger.get_logger()
