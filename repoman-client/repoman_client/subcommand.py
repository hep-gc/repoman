import os
import sys

# Import the RepomanCLI singleton instance:
from repoman_client.parsers import repoman_cli

class SubCommand(object):
    """A baseclass that all subcommands must be subclassed from.

    required methods:

        __call__(self, args)
            - This is the entry point that will be called to execute the
              subcommand.
            - args - contains the parsed commandline args
            What you do from this point on is up to you.

    """
    command = None # the command
    alias = None # a short alias for the command
    description = "" # a description string that will show up in a

    validate_config = True      # If False, config.validate() will not be called
                                # before the subcommand is run.
                                # If the subcommand depends on configuration values
                                # this should remain True.
    parser = None;

    def __init__(self):
        self.parser = repoman_cli.get_subparser().add_parser(self.command, help = self.description)
        self.init_parser()

    def init_parser(self):
        # Raise an exception to make sure people override this in the subclass
        raise Exception("You need to override the 'init_parser' class method")

    def __call__(self, args):
        # Raise an exception to make sure people override this in the subclass
        raise Exception("You need to override the '__call__' class method")

    def print_help(self):
        self.parser.print_help()

