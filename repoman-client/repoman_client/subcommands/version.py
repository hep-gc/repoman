import ConfigParser
import sys
from repoman_client.subcommand import SubCommand
from argparse import ArgumentParser
from repoman_client.parsers import repoman_cli

class Version(SubCommand):
    validate_config = False
    command = 'version'
    description = 'Show the repoman client version and exit.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_parser(self):
        self.parser.set_defaults(func=self)

    def __call__(self, args):
        print '1.0'
        sys.exit(0)

