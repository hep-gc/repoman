import os
import sys
from repoman_client.logger import log
from repoman_client.client import RepomanClient
from repoman_client.config import config

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
    usage = None # the command usage; override this only if needed
    short_description = None
    description = "" # a description string that will show up in a

    arg_parser = None;

    def __init__(self):
        h = None
        if self.short_description:
            h = self.short_description
        else:
            h = self.description

        self.arg_parser = repoman_cli.get_sub_arg_parser().add_parser(self.command, 
                                                                      description = self.description,
                                                                      help = h, 
                                                                      usage = self.usage,
                                                                      add_help = False)
        self.init_arg_parser()

        self.get_arg_parser().set_defaults(func=self.delegator)

        if self.alias:
            alias_sp = repoman_cli.get_sub_arg_parser().add_parser(self.alias,
                                                                   description = self.description,
                                                                   help = "Alias for %s" % (self.command),
                                                                   usage = self.usage,
                                                                   add_help=False, 
                                                                   parents=[self.arg_parser])

    def init_arg_parser(self):
        # Raise an exception to make sure people override this in the subclass
        raise NotImplementedError("You need to override the 'init_arg_parser' class method")

    def validate_args(self, args):
        # Default implementation is to do no validation on the arguments.
        # Override this method in the child class where needed and it will
        # automatically get called.
        #
        # Implementations of this method should throw a RepomanInvalidArgument
        # exception when an argument fails validation.
        log.debug('No argument validation implemented for the %s subcommand.' % (self.command))

    def get_arg_parser(self):
        return self.arg_parser

    # Subclasses can you this method to easily use a RepomanClient instance to
    # make calls to the repoman server.
    # It currently creates a new instance everytime it is called.  If needed, we
    # could implement some caching method with lazy instantiation in here.
    def get_repoman_client(self, args = None):
        host = config.host
        port = config.port
        proxy = config.proxy
        if args:
            if args.repository:
                host = args.repository
            if args.port:
                port = args.port
            if args.proxy:
                proxy = args.proxy
        return RepomanClient(host, port, proxy)

    # This method gets called when the sub command is parsed.
    # It should simply delegate the work to the subcommand by
    # calling the subcommand's __call__ method.
    def delegator(self, args):
        log.info('repoman subcommand called: %s' % (self.command))
        log.debug('args: %s' % (args))
        # Validate CLI arguments first
        log.debug('Validating arguments...')
        self.validate_args(args)
        # Now we can delegate to the child class
        self.__call__(args)


    def __call__(self, args):
        # Raise an exception to make sure people override this in the subclass
        raise NotImplementedError("You need to override the '__call__' class method")

    def print_help(self):
        self.arg_parser.print_help()

