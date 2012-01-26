import ConfigParser
import os
import sys
import logging
from repoman_client.utils import get_userid

DEFAULT_CONFIG_TEMPLATE="""\
# Configuration file for the repoman client scripts

[Repository]
#
# repository: Fully qualified domain name of the host that the Repoman
#                  repository resides on. (ie, localhost or vmrepo.tld.org)
#repository: %(repository)s

#
# port: Port number that Repoman repsoitory is being served on
#
#port: %(port)d


[User]
#
# proxy_cert: Full path to an RFC compliant proxy certificate.
#             Order of proxy certificate precedence:
#                       1. command line '-P|--proxy' argument
#                       2. value in this file
#                       3. $X509_USER_PROXY
#                       4. /tmp/x509up_u`id -u` 
#                       Note: Item 4 above will respect $SUDO_UID if available
#
#proxy_cert: %(proxy_cert)s


[Logger]
#
# enabled:          If True, then logs will be generated and placed in 'dir'
#
#enabled: %(logging_enabled)s

#
# dir:              Name of directory that logs will be placed in.
#                   If this is NOT an absolute path, then the directory is
#                   assumed to reside in the base directory of this config file.
#                   Defaults to '$HOME'/.repoman/logs
#
#dir: %(logging_dir)s

#
# The logging level.
# Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Defaults to INFO
#
#level: %(logging_level)s



[ThisImage]
#
# lockfile:        The lockfile used by Repoman to synchronize the image
#                  snapshot process.
#
#lockfile: %(lockfile)s

#
# snapshot:        Full path to a file that will be created to snapshot the
#                  running system to. (ie, /tmp/fscopy.img)
#
#snapshot: %(snapshot)s

#
# mountpoint:      Full path that 'snapshot' will be mounted at. (ie, /tmp/fscopy)
#
#mountpoint: %(mountpoint)s

#system_excludes: %(system_excludes)s
#user_excludes: %(user_excludes)s
"""





class Config(object):
    config_defaults = {'repository' : '',
                       'port' : 443,
                       'proxy_cert' : '',
                       'logging_enabled' : True,
                       'logging_dir' : '$HOME/.repoman/logs',
                       'logging_level' : 'INFO', 
                       'lockfile' : '/tmp/repoman-sync.lock',
                       'snapshot' : '/tmp/fscopy.img',
                       'mountpoint' : '/tmp/fscopy',
                       'system_excludes' : '/cvmfs/* /dev/* /mnt/* /proc/* /root/.ssh /sys/* /tmp/*',
                       'user_excludes' : ''}


    def __init__(self):
        # The internal configuration value container.  In this case, we use
        # a ConfigParser object.
        self._config = None

        self.files_parsed = None

        # The possible paths of configuration files.
        # These path can include env variables.
        self._global_config_file = os.path.expandvars('/etc/repoman/repoman.conf')
        self._user_config_file = os.path.expandvars('$HOME/.repoman/repoman.conf')
        self._config_env_var = os.path.expandvars('$REPOMAN_CLIENT_CONFIG')


        # Read the config files
        self._read_config()

        # Validate
        self._validate()



    # Read the config files and populate the internal ConfigParser
    # instance.
    # It will attempt to read the config files in the following order:
    #  1. the global config file
    #  2. the file pointed to by the config file env variable
    #  3. the user's config file
    #
    # This method will exit with an error if a config file exist and could not be
    # parsed successfully.
    def _read_config(self):
        self._config = ConfigParser.ConfigParser()
        try:
            self.files_parsed = self._config.read([self._global_config_file,
                                              self._config_env_var,
                                              self._user_config_file])
        except Exception, e:
            print 'Error reading configuration file(s).\n%s' % (e)
            sys.exit(1)

        if len(self.files_parsed) == 0:
            print 'Could not find a repoman configuration file on your system.'
            print 'Please run "repoman make-config" to create a configuration file.'

            
    # Validates the current configuration.
    def _validate(self):
        pass

        
    # shortcut properties
    @property
    def host(self):
        if self._config.has_option('Repository', 'repository') and len(self._config.get('Repository', 'repository')) > 0:
            return self._config.get('Repository', 'repository')
        else:
            print 'Missing repository entry in repoman configuration.\nPlease edit the repository entry in your repoman configuration file and try again.'
            sys.exit(1)

    @property
    def port(self):
        if self._config.has_option('Repository', 'port'):
            return self._config.getint('Repository', 'port')
        else:
            return self.config_defaults['port']

    @property
    def proxy(self):
        if self._config.has_option('User', 'proxy_cert'):
            return self._config.get('User', 'proxy_cert')
        else:
            default_proxy = os.environ.get('X509_USER_PROXY')
            if not default_proxy:
                default_proxy = "/tmp/x509up_u%s" % get_userid()
            return default_proxy

    @property
    def logging_enabled(self):
        if not self._config.has_section('Logger') or not self._config.has_option('Logger', 'enabled'):
            return self.config_defaults['logging_enabled']
        return self._config.getboolean('Logger', 'enabled')

    @property
    def logging_dir(self):
        if self._config.has_section('Logger') and self._config.has_option('Logger', 'dir'):
            return self._config.get('Logger', 'dir')
        else:
            return os.path.expandvars(self.config_defaults['logging_dir'])

    @property
    def logging_level(self):
        level_string = None
        if self._config.has_section('Logger') and self._config.has_option('Logger', 'level'):
            level_string = self._config.get('Logger', 'level')
        else:
            level_string = self.config_defaults['logging_level']

        numeric_level = getattr(logging, level_string.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        else:
            return numeric_level

    @property
    def lockfile(self):
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'lockfile'):
            return self._config.get('ThisImage', 'lockfile')
        else:
            return self.config_defaults['lockfile']

    @property
    def snapshot(self):
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'snapshot'):
            return self._config.get('ThisImage', 'snapshot')
        else:
            return self.config_defaults['snapshot']

    @property
    def mountpoint(self):
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'mountpoint'):
            return self._config.get('ThisImage', 'mountpoint')
        else:
            return self.config_defaults['mountpoint']

    @property
    def system_excludes(self):
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'system_excludes'):
            return self._config.get('ThisImage', 'system_excludes')
        else:
            return self.config_defaults['system_excludes']

    @property
    def user_excludes(self):
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'user_excludes'):
            return self._config.get('ThisImage', 'user_excludes')
        else:
            return self.config_defaults['user_excludes']


    def files_parsed(self):
        return self.files_parsed


    # This method will generate the default config and try to write it
    # to the path defined by self._user_config_file.
    def generate_config(self, args):
        # Override default with given command line args
        values = self.config_defaults.copy()
        if args.system_excludes:
            values['system_excludes'] = args.system_excludes
        if args.user_excludes:
            values['user_excludes'] = args.user_excludes
        if args.repository:
            values['repository'] = args.repository
        if args.port:
            values['port'] = args.port
        if args.proxy:
            values['proxy_cert'] = args.proxy

        config_content = DEFAULT_CONFIG_TEMPLATE % values

        if args.stdout:
            print config_content
        else:
            # Create destination directory if needed
            if not os.path.isdir(os.path.dirname(self._user_config_file)):
                try:
                    os.makedirs(os.path.dirname(self._user_config_file))
                except OSError, e:
                    print 'Error creating configuration target directory.\n%s ' % (e)
                    sys.exit(1)

            # Write the config file if it does not already exist
            if os.path.isfile(self._user_config_file):
                print '%s already exist.  Not overwriting.' % (self._user_config_file)
                sys.exit(1)

            try:
                f = open(self._user_config_file, 'w')
                f.write(config_content)
                f.close()
                print 'Repoman configuration file written to %s' % (self._user_config_file)
            except Exception, e:
                print 'Error writing Repoman configuration file at %s\n%s' % (self._user_config_file, e)
                sys.exit(1)
        


# Globally accessible Config() singleton instance.
config = Config()

