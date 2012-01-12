import os
import sys
import logging

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
    arg_parser = None;

    def __init__(self):
        self.arg_parser = repoman_cli.get_sub_arg_parser().add_parser(self.command, 
                                                                      description = self.description,
                                                                      help = self.description, 
                                                                      add_help = False)
        self.init_arg_parser()
        if self.alias:
            alias_sp = repoman_cli.get_sub_arg_parser().add_parser(self.alias,
                                                                   help = self.description,
                                                                   description = self.description,
                                                                   add_help=False, 
                                                                   parents=[self.arg_parser])

    def init_arg_parser(self):
        # Raise an exception to make sure people override this in the subclass
        raise Exception("You need to override the 'init_arg_parser' class method")

    def get_arg_parser(self):
        return self.arg_parser

    def __call__(self, args):
        # Raise an exception to make sure people override this in the subclass
        raise Exception("You need to override the '__call__' class method")

    def print_help(self):
        self.arg_parser.print_help()

