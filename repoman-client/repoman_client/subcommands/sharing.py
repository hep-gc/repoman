from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from argparse import ArgumentParser
import sys

class ShareImage(SubCommand):
    command_group = 'advanced'
    command = 'share-image'
    alias = 'si'
    description = 'Share an image with users or groups'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('image', help='Image you want to share')
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument('-u', '--user', help='User to share with')
        g.add_argument('-g', '--group', help='Group to share with')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        status = "Shared image: '%s' with: '%s'"
        if args.user:
            func = repo.share_with_user
            kwargs = {'user':args.user}
            status = status % (args.image, args.user)
        elif args.group:
            func = repo.share_with_group
            kwargs = {'group':args.group}
            status = status % (args.image, args.group)
        else:
            kwargs = {}


        try:
            func(args.image, **kwargs)
            print "[OK]     %s" % status
        except RepomanError, e:
            print "[FAILED] %s\n\t-%s" % (status, e)
            sys.exit(1)



class UnshareImage(SubCommand):
    command_group = 'advanced'
    command = 'unshare-image'
    alias = 'ui'
    description = 'Remove a share from an image'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('image', help='Image to unshare')
        g = p.add_mutually_exclusive_group()
        g.add_argument('-u', '--user', help='User to remove share from')
        g.add_argument('-g', '--group', help='Group to remove share from')
        #g.add_argument('-a', '--all', help='Remove all shares')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        status = "Unshared image: '%s' with: '%s'"
        if args.user:
            func = repo.unshare_with_user
            kwargs = {'user':args.user}
            status = status % (args.image, args.user)
        elif args.group:
            func = repo.unshare_with_group
            kwargs = {'group':args.group}
            status = status % (args.image, args.group)
        else:
            kwargs = {}

        try:
            func(args.image, **kwargs)
            print "[OK]     %s" % status
        except RepomanError, e:
            print "[FAILED] %s\n\t-%s" % (status, e)
            sys.exit(1)

