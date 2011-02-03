import ConfigParser
import os
import sys
import subprocess

DEFAULT_CONFIG="""\
# Configuration file for the repoman client scripts
[Logger]
# NOTE: Logging is currently not implimented.  enabling logging will not yield 
#       any logs yet.
#
# enabled:          If True, then logs will be generated and placed in 'log_dir'
# log_dir:          Name of directory that logs will be placed in.
#                   If this is NOT an absolute path, then the directory is
#                   assumed to reside in the base directory of this config file.
# 
logging_enabled: true
logging_dir: repoman_logs


[Repository]
# repository_host: Fully qualified domain name of the host that the Repoman
#                  repository resides on. (ie, localhost or vmrepo.tld.org)
#
# repository_port: Port number that Repoman repsoitory is being served on
#
repository_host:
repository_port: 443


[User]
# user_proxy_cert: Full path to an RFC compliant proxy certificate.
#                  If not specified, this will default to /tmp/x509up_u`id -u`
#
user_proxy_cert:


[ThisImage]
# snapshot:        Full path to a file that will be created to snapshot the
#                  running system to. (ie, /tmp/fscopy.img)
#
# mountpoint:      Full path that 'snapshot' will be mounted at. (ie, /tmp/fscopy)
#
# exclude_dirs:    A list of directories that will be excluded when creating the
#                  snapshot of the running system.
#                  Each directory must be the full path.
#                  Each item in the list is seperated by a space.
#
lockfile: /tmp/repoman-sync.lock
snapshot: /tmp/fscopy.img
mountpoint: /tmp/fscopy
exclude_dirs: /dev /mnt /lustre /proc /sys /tmp /etc/grid-security /root/.ssh
"""


class Config(object):
    def __init__(self, config_file=None):
        self._errors_found = False
        self._error_messages = []
        self.required_options = [('Repository', 'repository_host'),
                                 ('Repository', 'repository_port'),
                                 ('User', 'user_proxy_cert'),
                                 ('ThisImage', 'mountpoint'),
                                 ('ThisImage', 'snapshot'),
                                 ('ThisImage', 'exclude_dirs'),
                                 ('ThisImage', 'lockfile'),
                                 ('Logger', 'logging_enabled'),
                                 ('Logger', 'logging_dir')]

        self._config_locations = ['$REPOMAN_CLIENT_CONFIG',
                                  '$HOME/.repoman/repoman.conf',
                                  '~/.repoman/repoman.conf']

        if config_file:
            self._config_locations.insert(0, config_file)

        self._default_config_dir = os.path.expanduser('~/.repoman')
        self._default_proxy = "/tmp/x509up_u%s" % os.getuid()

        #Read the config file if possible
        self._read_config()
        self._check_logging()

    #short cut properties
    @property
    def host(self):
        return self.repository_host

    @property
    def port(self):
        return self.repository_port

    @property
    def proxy(self):
        return self.user_proxy_cert

    def validate(self, verbose=False, exit=True):
        self.verbose = verbose
        if not self.config_file:
            print "No configuration file found."
            sys.exit(1)
        self._validate_options()
        self._check_logging()
        self._check_proxy()
        if self._errors_found:
            for error in self._error_messages:
                print error
            if exit:
                sys.exit(1)

    def generate_config(self):
        if not os.path.isdir(self._default_config_dir):
            try:
                os.mkdir(self._default_config_dir)
            except:
                print "Unable to create configuration directory at '%s'" % self._default_config_dir
                sys.exit(1)

        try:
            config_file = os.path.join(self._default_config_dir, 'repoman.conf')
            config = open(config_file, 'w')
            config.write(DEFAULT_CONFIG)
            self.config_file = config_file
        except:
            print "Unable to generate configuration in '%s'" % self._config_dir
            sys.exit(1)

    def _check_logging(self):
        if not self.logging_enabled:
            return
        elif self.logging_enabled and not self.logging_dir:
            self._error_messages = True
            self._error_messages.append("Specify a logging directory")
            return
        elif not os.path.isabs(self.logging_dir):
            self.logging_dir = os.path.join(os.path.dirname(self.config_file),
                                            self.logging_dir)

        if not os.path.isdir(self.logging_dir):
            try:
                os.mkdir(self.logging_dir)
            except:
                self._errors_found = True
                self._error_messages.append("Logging dir does not exist and I am unable to create it.")

        test_file = os.path.join(self.logging_dir, 'TEST_LOG.DELETE_ME')
        try:
            test = open(test_file, 'w')
            test.close()
            os.remove(test_file)
        except:
            self._errors_found = True
            self._error_messages.append("The logging directory is not writable.")

    def _validate_options(self):
        for option in self.required_options:
            if not getattr(self, option[1], None):
                self._errors_found = True
                self._error_messages.append("You must set the '%s' config value in '%s'" % (option[1], self.config_file))

    def _get_config_file(self):
        for cfg in self._config_locations:
            cfg = os.path.expandvars(os.path.expanduser(cfg))
            if os.path.isfile(cfg):
                self.config_file = cfg
                return cfg
        self.config_file = None
        return ''

    def _read_config(self):
        config_file = self._get_config_file()
        config = ConfigParser.ConfigParser()
        try:
            config.read(config_file)
        except ConfigParser.MissingSectionHeaderError:
            self._errors_found = True
            self._error_messages.append("The specified config file is poorly formatted.")
        except Exception:
            self._errors_found = True
            self._error_messages.append("Unable to open config file")

        for option in self.required_options:
            if config.has_option(option[0], option[1]):
                value = config.get(option[0], option[1])
                if value.isdigit():
                    value = int(value)
                setattr(self, option[1], value)
            else:
                setattr(self, option[1], None)

        if not self.user_proxy_cert:
            self.user_proxy_cert = self._default_proxy

    def _check_proxy(self):
        if not os.path.isfile(self.user_proxy_cert):
            self._errors_found = True
            self._error_messages.append("The proxy certificate: '%s' does not exist.\nGenerate a new cert or manually specify with '--proxy'" % self.user_proxy_cert)
            return

        # Test expiration
        cmd = "openssl x509 -in %s -noout -checkend 0" % self.user_proxy_cert
        retcode = subprocess.call(cmd, shell=True)
        if retcode:
            self._errors_found = True
            self._error_messages.append("The proxy certificate: '%s' is expired" % self.user_proxy_cert)


config = Config()

