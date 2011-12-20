import ConfigParser
from repoman_client.subcommand import SubCommand
from argparse import ArgumentParser
from repoman_client.parsers import repoman_cli

class Help(SubCommand):
    validate_config = False
    command = 'help'
    description = 'This is the help command.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_parser(self):
        self.parser.add_argument('helpcommand', nargs='?')
        self.parser.set_defaults(func=self)

    def __call__(self, args):
        print args
        repoman_cli.print_help(args.helpcommand)

