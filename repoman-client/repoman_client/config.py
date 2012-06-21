import ConfigParser
import os
import sys
import logging
from repoman_client.utils import get_userid
from repoman_client.exceptions import RepomanError, ClientConfigurationError

DEFAULT_CONFIG_TEMPLATE="""\
# Configuration file for the repoman client scripts

[Repository]
#
# repository: Fully qualified domain name of the host that the Repoman
#             repository resides on. (ie, localhost or vmrepo.tld.org)

#repository: %(repository)s

#
# port: Port number that Repoman repsoitory is being served on.
#       Default: %(port)d
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
# enabled:          If True, then logs will be generated and placed in the
#                   location defined by 'dir'.
#                   Default: %(logging_enabled)s
#
#enabled: %(logging_enabled)s

#
# dir:              Name of directory that logs will be placed in.
#                   If this is NOT an absolute path, then the directory is
#                   assumed to reside in the base directory of this config file.
#                   Default: %(logging_dir)s
#
#dir: %(logging_dir)s

#
# The logging level.
# Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Default: %(logging_level)s
#
#level: %(logging_level)s



[ThisImage]

#
# snapshot_dir:    The location where the lockfile, snapshot and mountpoint
#                  will be created.
#                  Default: %(snapshot_dir)s
#
#snapshot_dir: %(snapshot_dir)s

#
# system_excludes:  Blank separated list of paths to be excluded from a snapshot 
#                   of the operating system during a repoman save-image.  A
#                   directory path specification ending in '/*' will cause
#                   the directory to be created in the saved image, but none
#                   of it's contents to be copied to the saved image.
#                   Default: %(system_excludes)s
#
# * WARNING: Please edit this variable only if you really unserstand what
# you are doing. *
#
#system_excludes: %(system_excludes)s

#
# user_excludes:  Blank separated list of paths to be excluded from 
#                 a snapshot of the operating system during a repoman 
#                 save-image.  A directory path specification ending in
#                 '/*' will cause the directory to be created in the 
#                 saved image, but none of it's contents to be copied to
#                 the saved image.  Defaults to an empty list.
#
#                 Note: The system-excludes and user-excludes parameters 
#                 perform precisely the same function.  However, because 
#                 certain specifications are required to create a functional
#                 image, these specifications are established by default in
#                 the system-excludes parameter. It is recommended that
#                 other exclusions be made by modifying the user-excludes
#                 parameter only.
#
#user_excludes: %(user_excludes)s


"""





class Config(object):
    _instance = None

    @staticmethod
    def get_instance():
        if Config._instance == None:
            Config._instance = Config()
        return Config._instance

    # The following data struture will hold the default values for the
    # repoman client configuration.
    # If you need to change a default value, do it here, as this will also
    # affect the default configuration file generation.
    #
    config_defaults = {'repository' : '',
                       'port' : 443,
                       'proxy_cert' : '',
                       'logging_enabled' : True,
                       'logging_dir' : '$HOME/.repoman/logs',
                       'logging_level' : 'INFO',
                       'snapshot_dir' : '/tmp',
                       'lockfile' : 'repoman-sync.lock',
                       'snapshot' : 'repoman-fscopy.img',
                       'mountpoint' : 'repoman-fscopy',
                       'system_excludes' : '/dev/* /mnt/* /proc/* /root/.ssh /sys/* /tmp/*',
                       'user_excludes' : '',
                       'restricted_path' : '/bin:/usr/bin:/usr/local/bin:/sbin:/usr/sbin:/usr/local/sbin'}


    def __init__(self):

        # The internal configuration value containers.  In this case, we use
        # a ConfigParser object.
        # We have 2 configuration containers: 1 for the system-wide
        # configuration only, and a second one which is for the combination of
        # all configuration files parsed.
        self._global_config = None
        self._config = None
        
        self.files_parsed = None

        # The possible paths of configuration files.
        # These path can include env variables.
        self._global_config_file = os.path.expandvars('/etc/repoman/repoman.conf')
        if 'SUDO_UID' in os.environ:
            self._user_config_file = os.path.expanduser('~%s/.repoman/repoman.conf' % os.environ.get('SUDO_USER'))
        else:
            self._user_config_file = os.path.expanduser('~/.repoman/repoman.conf')
        self._config_env_var = os.path.expandvars('$REPOMAN_CLIENT_CONFIG')

        self.files_parsed = self._read_config()
        if len(self.files_parsed) > 0:
            self._validate()


    # Read the config files and populate the internal ConfigParser
    # instance.
    # It will attempt to read the config files in the following order:
    #  1. the global config file
    #  2. the file pointed to by the config file env variable
    #  3. the user's config file
    #
    # Returns a list of config files successfully parsed.
    #
    # This method will exit with an error if a config file exist that 
    # could not be parsed successfully.
    def _read_config(self):
        self._config = ConfigParser.ConfigParser()
        self._global_config = ConfigParser.ConfigParser()

        # Try to read the global config alone first.
        try:
            files_parsed = self._global_config.read([self._global_config_file])
            if len(files_parsed) == 0:
                self._global_config = None

        except Exception, e:
            raise ClientConfigurationError('Error reading configuration file(s).\n%s' % (e))

        # Now try to read all the config files.
        try:
            files_parsed = self._config.read([self._global_config_file,
                                              self._config_env_var,
                                              self._user_config_file])
            return files_parsed

        except Exception, e:
            raise ClientConfigurationError('Error reading configuration file(s).\n%s' % (e))

            
    # Validates the current configuration.
    def _validate(self):
        pass

        
    # shortcut properties
    @property
    def host(self):
        if len(self.files_parsed) == 0:
            raise ClientConfigurationError('Could not find a repoman configuration file on your system.\nPlease run "repoman make-config" to create a configuration file.')
            
        if self._config.has_option('Repository', 'repository') and len(self._config.get('Repository', 'repository')) > 0:
            return self._config.get('Repository', 'repository')
        else:
            raise ClientConfigurationError('Missing repository entry in repoman configuration [%s].\nPlease edit the repository entry in your repoman configuration file and try again.' % (self.files_parsed[-1]))

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
    def snapshot_dir(self):
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'snapshot_dir'):
            return self._config.get('ThisImage', 'snapshot_dir')
        else:
            return self.config_defaults['snapshot_dir']

    @property
    def lockfile(self):
        v = None
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'lockfile'):
            v = self._config.get('ThisImage', 'lockfile')
        else:
            v = self.config_defaults['lockfile']

        # Prepend snapshot_dir if not absolute path.
        if not os.path.isabs(v):
            v = os.path.join(self.snapshot_dir, v)

        return v


    @property
    def snapshot(self):
        v = None
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'snapshot'):
            v = self._config.get('ThisImage', 'snapshot')
        else:
            v = self.config_defaults['snapshot']

        # Prepend snapshot_dir if not absolute path.
        if not os.path.isabs(v):
            v = os.path.join(self.snapshot_dir, v)

        return v

    @property
    def mountpoint(self):
        v = None
        if self._config.has_section('ThisImage') and self._config.has_option('ThisImage', 'mountpoint'):
            v = self._config.get('ThisImage', 'mountpoint')
        else:
            v = self.config_defaults['mountpoint']

        # Prepend snapshot_dir if not absolute path.
        if not os.path.isabs(v):
            v = os.path.join(self.snapshot_dir, v)

        return v

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

    # Change this method's return value if you need to change the acceptable
    # image name syntax.  
    def get_image_name_regex(self):
        return '^[a-zA-Z0-9_\-\.]+$'



    # This method will generate the default config and try to write it
    # to the path defined by self._user_config_file.
    def generate_config(self, args):
        values = self.config_defaults.copy()

        config_content = DEFAULT_CONFIG_TEMPLATE % values

        if args.stdout:
            print config_content
        else:
            # Create destination directory if needed
            if not os.path.isdir(os.path.dirname(self._user_config_file)):
                try:
                    os.makedirs(os.path.dirname(self._user_config_file))
                except OSError, e:
                    raise ClientConfigurationError('Error creating configuration target directory.\n%s ' % (e))

            # Make a backup of the existing config file if present
            if os.path.isfile(self._user_config_file):
                backup_file = self._user_config_file + '.bak'
                os.rename(self._user_config_file, backup_file)
                print 'Note: Existing config file has been copied to %s' % (backup_file)

            try:
                f = open(self._user_config_file, 'w')
                f.write(config_content)
                f.close()
                print 'New repoman configuration file written to %s' % (self._user_config_file)
            except Exception, e:
                raise ClientConfigurationError('Error writing Repoman configuration file at %s\n%s' % (self._user_config_file, e))
        

    def get_restricted_env(self):
        """
        This method will return a restricted environment to be used when
        making subprocess calls which require enhanced security.
        (i.e., which are run as sudo)
        Note that only the system-wide repoman config file will be
        consulted for the restricted environment settings.
        If no system-wide repoman configuration file is present, then
        a default restricted environment will be used.
        """
        restricted_path = self.config_defaults['restricted_path']
        if self._global_config and self._global_config.has_section('Security') and self._global_config.has_option('Security', 'restricted_path'):
            restricted_path = self._global_config.get('Security', 'restricted_path')

        restricted_env = os.environ.copy()
        restricted_env['PATH'] = restricted_path
        return restricted_env

        
# Globally accessible Config() singleton instance.
config = None
try:
    config = Config.get_instance()
except RepomanError, e:
    print e
    sys.exit(1)

