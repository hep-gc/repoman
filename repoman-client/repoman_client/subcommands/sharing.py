from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from argparse import ArgumentParser
import sys
import logging

class ShareImageWithGroups(SubCommand):
    command = 'share-image-with-groups'
    alias = 'sig'
    description = 'Share an image with one or more groups.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The image to share. Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('group', nargs = '+', help = 'The name of the group(s) to share the image with. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for group in args.group:
            try:
                kwargs = {'group':group}
                if args.owner:
                    repo.share_with_group(args.owner + '/' + args.image, **kwargs)
                else:
                    repo.share_with_group(args.image, **kwargs)

                print "[OK]     Shared image: '%s' with group: '%s'" % (args.image, group)
            except RepomanError, e:
                print "[FAILED] Shared image: '%s' with group: '%s'\n\t-%s" % (args.image, group, e)
                sys.exit(1)


class ShareImageWithUsers(SubCommand):
    command = 'share-image-with-users'
    alias = 'siu'
    description = 'SShare an image with one or more users.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The image to share. Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('user', nargs = '+', help = 'The name of the users(s) to share the image with. Use "repoman list-users" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for user in args.user:
            try:
                kwargs = {'user':user}
                if args.owner:
                    repo.share_with_user(args.owner + '/' + args.image, **kwargs)
                else:
                    repo.share_with_user(args.image, **kwargs)

                print "[OK]     Shared image: '%s' with user: '%s'" % (args.image, user)
            except RepomanError, e:
                print "[FAILED] Shared image: '%s' with user: '%s'\n\t-%s" % (args.image, user, e)
                sys.exit(1)



class UnshareImageWithGroups(SubCommand):
    command = 'unshare-image-with-groups'
    alias = 'uig'
    description = 'Unshare an image with one or more groups.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help='The image to unshare. Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('group', nargs = '+', help='The name of the group(s) to unshare the image with. Use "repoman describe-image" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for group in args.group:
            try:
                kwargs = {'group':group}
                if args.owner:
                    repo.unshare_with_group(args.owner + '/' + args.image, **kwargs)
                else:
                    repo.unshare_with_group(args.image, **kwargs)

                print "[OK]     Unshared image: '%s' with group: '%s'" % (args.image, group)
            except RepomanError, e:
                print "[FAILED] Unsharing image: '%s' with group: '%s'\n\t-%s" % (args.image, group, e)
                sys.exit(1)


class UnshareImageWithUsers(SubCommand):
    command = 'unshare-image-with-users'
    alias = 'uiu'
    description = 'Unshare an image with one or more users.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help='The image to unshare. Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('user', nargs = '+', help='The name of the user(s) to unshare the image with. Use "repoman describe-image" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for user in args.user:
            try:
                kwargs = {'user':user}
                if args.owner:
                    repo.unshare_with_user(args.owner + '/' + args.image, **kwargs)
                else:
                    repo.unshare_with_user(args.image, **kwargs)

                print "[OK]     Unshared image: '%s' with user: '%s'" % (args.image, user)
            except RepomanError, e:
                print "[FAILED] Unsharing image: '%s' with user: '%s'\n\t-%s" % (args.image, user, e)
                sys.exit(1)



