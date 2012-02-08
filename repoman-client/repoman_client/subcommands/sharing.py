from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.config import config
from repoman_client.exceptions import RepomanError, SubcommandFailure
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
        self.get_arg_parser().add_argument('groups', help = 'Comma separated list of the groups to share the image with. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        for group in args.groups.split(','):
            try:
                kwargs = {'group':group}
                if args.owner:
                    self.get_repoman_client(args).share_with_group(args.owner + '/' + args.image, **kwargs)
                else:
                    self.get_repoman_client(args).share_with_group(args.image, **kwargs)

                print "[OK]     Shared image: '%s' with group: '%s'" % (args.image, group)
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not share image: '%s' with group: '%s'" % (args.image, group), e)


class ShareImageWithUsers(SubCommand):
    command = 'share-image-with-users'
    alias = 'siu'
    description = 'Share an image with one or more users.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The image to share. Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('users', help = 'Comma separated list of the users to share the image with. Use "repoman list-users" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        for user in args.users.split(','):
            try:
                kwargs = {'user':user}
                if args.owner:
                    self.get_repoman_client(args).share_with_user(args.owner + '/' + args.image, **kwargs)
                else:
                    self.get_repoman_client(args).share_with_user(args.image, **kwargs)

                print "[OK]     Shared image: '%s' with user: '%s'" % (args.image, user)
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not share image: '%s' with user: '%s'" % (args.image, user), e)



class UnshareImageWithGroups(SubCommand):
    command = 'unshare-image-with-groups'
    alias = 'uig'
    description = 'Unshare an image with one or more groups.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help='The image to unshare. Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('groups', help='Comma separated list of the group(s) to unshare the image with. Use "repoman describe-image" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        for group in args.groups.split(','):
            try:
                kwargs = {'group':group}
                if args.owner:
                    self.get_repoman_client(args).unshare_with_group(args.owner + '/' + args.image, **kwargs)
                else:
                    self.get_repoman_client(args).unshare_with_group(args.image, **kwargs)

                print "[OK]     Unshared image: '%s' with group: '%s'" % (args.image, group)
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not unshare image: '%s' with group: '%s'" % (args.image, group), e)


class UnshareImageWithUsers(SubCommand):
    command = 'unshare-image-with-users'
    alias = 'uiu'
    description = 'Unshare an image with one or more users.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help='The image to unshare. Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('users', help='Comma separated list of the users to unshare the image with. Use "repoman describe-image" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        for user in args.users.split(','):
            try:
                kwargs = {'user':user}
                if args.owner:
                    self.get_repoman_client(args).unshare_with_user(args.owner + '/' + args.image, **kwargs)
                else:
                    self.get_repoman_client(args).unshare_with_user(args.image, **kwargs)

                print "[OK]     Unshared image: '%s' with user: '%s'" % (args.image, user)
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not unshare image: '%s' with user: '%s'" % (args.image, user), e)
