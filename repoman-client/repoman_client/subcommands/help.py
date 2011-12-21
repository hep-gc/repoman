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

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('helpcommand', nargs='?')
        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repoman_cli.print_help(args.helpcommand)

