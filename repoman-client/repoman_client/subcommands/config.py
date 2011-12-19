import ConfigParser
from repoman_client.subcommand import SubCommand
from repoman_client.config import config

class MakeConfig(SubCommand):
    validate_config = False

    def __call__(self, args):
        print "Generating new default configuration file"
        config.generate_config()
        print "Customization can be done be editing '%s'" % config.config_file


