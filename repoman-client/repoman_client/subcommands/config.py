import ConfigParser
from repoman_client.subcommand import SubCommand
from repoman_client.config import config
from argparse import ArgumentParser

class MakeConfig(SubCommand):
    validate_config = False
    command = 'make-config'
    description = 'Create a repoman client configuration file under your home directory.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('repository', 
                                   help = 'The fully qualified domain name (FQDN) of the repoman image repository server to be managed.')
        self.get_arg_parser().add_argument('-p', '--port', 
                                   help = 'Used to specify the port that the repoman server listens on.')
        self.get_arg_parser().add_argument('-P', '--proxy', 
                                   help = 'The location of your proxy credential to be used when communicating with the repoman server.')
        self.get_arg_parser().add_argument('-E', '--system_excludes', 
                                   help = 'bla bla bla')
        self.get_arg_parser().add_argument('-e', '--excludes', 
                                   help = 'bla bla bla')
        self.get_arg_parser().set_defaults(func=self)



    def __call__(self, args):
        print "Generating new default configuration file"
        # do nothing for now as we debug this new system...
        #config.generate_config()
        #print "Customization can be done by editing '%s'" % config.config_file


