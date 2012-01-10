from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.subcommand import SubCommand
from repoman_client import display
from argparse import ArgumentParser
import sys
import logging
import ConfigParser

class DescribeUser(SubCommand):
    command = "describe-user"
    alias = "du"
    description = 'Display information about a repoman user'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('user', help = 'The user to describe.  Use "repoman list-users" to see possible values.')
        self.get_arg_parser().set_defaults(func=self)
        
    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            user = repo.describe_user(args.user)
            display.describe_user(user, long=True)
        except RepomanError, e:
            print e
            sys.exit(1)



class DescribeGroup(SubCommand):
    command_group = "advanced"
    command = "describe-group"
    alias = "dg"
    description = 'Display information about an existing group'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('group', help='Group to describe')
        p.add_argument('-l', '--long', action='store_true', default=False,
                       help='Display a long description of GROUP')
        return p

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('DescribeGroup')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
        
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            group = repo.describe_group(args.group)
            display.describe_group(group, long=args.long)
        except RepomanError, e:
            print e
            sys.exit(1)


class DescribeImage(SubCommand):
    command = "describe-image"
    alias = "di"
    description = 'Display information about an image'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help='The image to describe.  Use repoman list-images to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', help='The owner of the named image.  The default is the ID of the current repoman user which can be determined with the "repoman whoami" command.')
        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            image_path = args.image
            if args.owner:
                image_path = args.owner + '/' + args.image
            image = repo.describe_image(image_path)
            display.describe_image(image, long=True)
        except RepomanError, e:
            print e
            sys.exit(1)

