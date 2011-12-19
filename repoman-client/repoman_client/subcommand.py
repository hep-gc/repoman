import os
import sys



class SubCommand(object):
    """A baseclass that all subcommands must be subclassed from.

    required methods:

        __call__(self, args)
            - This is the entry point that will be called to execute the
              subcommand.
            - args - contains the parsed commandline args
            What you do from this point on is up to you.

    """
    validate_config = True      # If False, config.validate() will not be called
                                # before the subcommand is run.
                                # If the subcommand depends on configuration values
                                # this should remain True.
    require_sudo = False        # Will check to see that the user is sudo before
                                # executing command.                                

    def __call__(self, args):
        # Raise an exception to make sure people override this in the subclass
        raise Exception("You need to override the '__call__' class method")
