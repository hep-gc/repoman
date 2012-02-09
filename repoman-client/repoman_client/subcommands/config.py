import sys
import ConfigParser
from repoman_client.subcommand import SubCommand
from repoman_client.config import config

class MakeConfig(SubCommand):
    command = 'make-config'
    alias = 'mc'
    description = 'Create a repoman client configuration file under your home directory.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('--stdout', action='store_true', help = 'Send the configuration to stdout instead of writing it to a file under the current user\'s home directory.')


    def __call__(self, args):
        config.generate_config(args)
            
