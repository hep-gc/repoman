from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.exceptions import RepomanError, SubcommandFailure
from repoman_client.config import config
from repoman_client import display
from repoman_client.__version__ import version
from repoman_client.logger import repoman_logger
import sys

class Whoami(SubCommand):
    command = 'whoami'
    alias = None
    description = 'Display information about the current user (ie, you).'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        pass

    def __call__(self, args):
        try:
            me = self.get_repoman_client(args).whoami()
            print me.get('user_name')
        except RepomanError, e:
            raise SubcommandFailure(self, 'Error getting current user\'s information.', e)



class About(SubCommand):
    command = 'about'
    alias = None
    description = 'Display the repoman client version and configuration information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        pass

    def __call__(self, args):
        keys = {'config_file': ', '.join(config.files_parsed),
                'host':config.host,
                'port':config.port,
                'proxy':config.proxy,
                'snapshot':config.snapshot,
                'mountpoint':config.mountpoint,
                'lockfile':config.lockfile,
                'system_excludes':config.system_excludes,
                'user_excludes':config.user_excludes,
                'version':version}

        if not repoman_logger.is_enabled():
            keys['logging'] = 'Disabled'
        else:
            keys['logging'] = 'Log sent to: %s' % (repoman_logger.get_log_filename())

        print """\
     client version: %(version)s
config files in use: %(config_file)s
    repository_host: %(host)s
    repository_port: %(port)s
    user_proxy_cert: %(proxy)s
           snapshot: %(snapshot)s
         mountpoint: %(mountpoint)s
           lockfile: %(lockfile)s
    system_excludes: %(system_excludes)s
      user_excludes: %(user_excludes)s
            logging: %(logging)s
""" % keys

