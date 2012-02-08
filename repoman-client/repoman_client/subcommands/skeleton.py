from repoman_client.subcommand import SubCommand
from repoman_client.logger import log
from repoman_client.exceptions import InvalidArgumentError



#
# Use this skeleton class definition as a starting point for your new
# repoman subcommands.
#
# Simply make a copy of this file and edit it accordingly.
# Also don't forget to import your new class into the 
# repoman-client/repoman file and add an instance of it to 
# subcommand container, such as:
#   repoman_cli.add_subcommand(MyCommand())
#
class MyCommand(SubCommand):
    command = "mycommand"

    # The following attributes are optional.
    alias = 'mc'
    description = 'This is a full description of my command.'
    short_description = 'This is a shorter description of my command.'

    # Constructor.
    # In most cases you will not have to modify this.
    def __init__(self):
        SubCommand.__init__(self)

    # This method will automatically get called and should populate this
    # subcommand's ArgumentParser.
    def init_arg_parser(self):
        self.get_arg_parser().add_argument('foo', 
                                           help = 'foo help')

    # Implementing this method is optional.
    # It will get automatically called just before the command is executed.
    # It should raise a InvalidArgumentError exception when an argument does not
    # pass validation.
    def validate_args(self, args):
        if len(args.foo) < 8:
            raise InvalidArgumentError('Error: foo must be at least 8 characters long')

    # The __call__ method is where the work is being done.  It will
    # automatically get called and the command line arguments will get passed
    # in args.
    def __call__(self, args):
        # If you need to make a call to the repoman server, you can use the
        # self.get_repoman_client(args) method.

        log.info('foo subcommand called.')

        # TODO: Put your implementation code here...
        return
