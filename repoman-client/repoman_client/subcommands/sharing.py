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
        self.get_arg_parser().set_defaults(func=self)

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
        self.get_arg_parser().set_defaults(func=self)

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
        log = logging.getLogger('UnshareImage')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
    
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
        
        log.debug("kwargs: '%s'" % kwargs)

        try:
            func(args.image, **kwargs)
            print "[OK]     %s" % status
        except RepomanError, e:
            print "[FAILED] %s\n\t-%s" % (status, e)
            sys.exit(1)

