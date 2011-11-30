from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client import display
from repoman_client.__version__ import version
from argparse import ArgumentParser
import sys

class Whoami(SubCommand):
    command_group = 'advanced'
    command = 'whoami'
    alias = None
    description = 'Display information about the current user (ie, you)'

    def get_parser(self):
        p = ArgumentParser(self.description)
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            me = repo.whoami()
            print me.get('user_name')
        except RepomanError, e:
            print e
            sys.exit(1)



class About(SubCommand):
    validate_config = False
    command_group = 'advanced'
    command = 'about'
    alias = None
    description = 'Display information about this program.'

    def get_parser(self):
        p = ArgumentParser(self.description)
        return p

    def __call__(self, args, extra_args=None):
        keys = {'config_file':config.config_file,
                'host':config.repository_host,
                'port':config.repository_port,
                'proxy':config.user_proxy_cert,
                'snapshot':config.snapshot,
                'mountpoint':config.mountpoint,
                'exclude':config.exclude_dirs,
                'version':version}
        print """\
version:    %(version)s
configuration:
    config_file in use: %(config_file)s
    repository_host:    %(host)s
    repository_port:    %(port)s
    user_proxy_cert:    %(proxy)s
    snapshot:           %(snapshot)s
    mountpoint:         %(mountpoint)s
    exclude_dirs:       %(exclude)s
""" % keys

