from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.subcommand import SubCommand
from repoman_client import display
from argparse import ArgumentParser
import sys

class DescribeUser(SubCommand):
    command_group = "advanced"
    command = "describe-user"
    alias = "du"
    description = 'Display information about an existing user'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('user', help='User to describe')
        p.add_argument('-l', '--long', action='store_true', default=False,
                       help='Display a long description of USER')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            user = repo.describe_user(args.user)
            display.describe_user(user, long=args.long)
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
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            group = repo.describe_group(args.group)
            display.describe_group(group, long=args.long)
        except RepomanError, e:
            print e
            sys.exit(1)


class DescribeImage(SubCommand):
    command_group = "advanced"
    command = "describe-image"
    alias = "di"
    description = 'Display information about an existing image'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('image', help='Image to describe')
        p.add_argument('-l', '--long', action='store_true', default=False,
                       help='Display a long description of IMAGE')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            image = repo.describe_image(args.image)
            display.describe_user(image, long=args.long)
        except RepomanError, e:
            print e
            sys.exit(1)

