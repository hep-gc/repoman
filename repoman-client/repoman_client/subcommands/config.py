import ConfigParser
from repoman_client.subcommand import SubCommand
from repoman_client.config import config
from argparse import ArgumentParser

class MakeConfig(SubCommand):
    validate_config = False
    command = 'make-config'
    alias = 'mc'
    description = 'Generate a configuration file'

    def get_parser(self):
        p = ArgumentParser(self.description)
        return p

    def __call__(self, args, extra_args=None):
        print "Generating new default configuration file"
        config.generate_config()
        print "Customization can be done be editing '%s'" % config.config_file

