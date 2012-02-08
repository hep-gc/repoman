import argparse
from repoman_client.exceptions import RepomanError


class RepomanCLI(object):
    _instance = None

    @staticmethod
    def get_instance():
        if RepomanCLI._instance == None:
            RepomanCLI._instance = RepomanCLI()
        return RepomanCLI._instance

    def __init__(self):
        self.arg_parser = None
        self.sub_arg_parser = None
        self.subcommands = {}
        self._init_arg_parser()


    # This method will initialize the base command-line argument arg_parser and create
    # a sub_arg_parser instance ready to be populated with subcommands.
    #
    # It should only be called via the construtor of this class.
    def _init_arg_parser(self):
        self.arg_parser = argparse.ArgumentParser(add_help=False)

        self.arg_parser.add_argument('-r', '--repository', help = 'The repoman repository server to connect to.  Overrides the "repository" setting in the configuration file.')
        self.arg_parser.add_argument('-p', '--port', type = int, help = 'The repoman repository server port to connect to.  Overrides the "port" setting in the configuration file.  Defaults to 443.')
        self.arg_parser.add_argument('-P', '--proxy', help = 'The path to your proxy certificate to be used for authentication.  Overrides the "proxy" setting in the configuration file.  Defaults to "/tmp/x509up_uNNNN", where "NNNN" is your effective UID.')
        self.arg_parser.add_argument('--debug', action='store_true', default = False, help=argparse.SUPPRESS)

        self.sub_arg_parser = self.arg_parser.add_subparsers(title = 'Subcommands', 
                                                             dest = 'subcommand')

        
    def get_arg_parser(self):
        return self.arg_parser


    def get_sub_arg_parser(self):
        return self.sub_arg_parser


    # Prints the help of either the main arg_parser (if subcommand is None), or for a subcommand.
    def print_help(self, subcommand):
        if subcommand == None:
            self.arg_parser.print_help()
        elif subcommand in self.subcommands:
            self.subcommands[subcommand].print_help()
        else:
            print 'No help available for "%s".' % (subcommand)


    # Call this method to add a subcommand to the main arg_parser.
    def add_subcommand(self, subcommand):
        self.subcommands[subcommand.command] = subcommand
        if subcommand.alias != None:
            self.subcommands[subcommand.alias] = subcommand

# Singleton instance of RepomanCLI:
repoman_cli = None
try:
    repoman_cli = RepomanCLI.get_instance()
except RepomanError, e:
    print e
    sys.exit(1)

