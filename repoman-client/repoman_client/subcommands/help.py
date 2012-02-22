import ConfigParser
import argparse
from repoman_client.subcommand import SubCommand
from repoman_client.parsers import repoman_cli

class Help(SubCommand):
    command = 'help'
    description = 'This is the help command.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('helpcommand', nargs='?')
        self.get_arg_parser().add_argument('remainder', nargs=argparse.REMAINDER)

    def __call__(self, args):
        repoman_cli.print_help(args.helpcommand)

