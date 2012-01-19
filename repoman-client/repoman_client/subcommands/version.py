import ConfigParser
import sys
from repoman_client.subcommand import SubCommand
from repoman_client.parsers import repoman_cli
from repoman_client.__version__ import version

class Version(SubCommand):
    command = 'version'
    description = 'Show the repoman client version and exit.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        pass

    def __call__(self, args):
        print version
        sys.exit(0)

