from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client import display
import argparse
from argparse import ArgumentParser
import sys
import logging

class ListUsers(SubCommand):
    command = "list-users"
    alias = 'lu'
    description = 'List repoman users.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('-l', '--long', action = 'store_true', default = False, help = 'Display a table with extra information.')
        self.get_arg_parser().add_argument('-g', '--group', metavar = 'group', help = 'Only display users that belong to the given group.')
        self.get_arg_parser().set_defaults(func=self)


    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if args.group:
            kwargs = {'group':args.group}
        else:
            kwargs = {}
            
        try:
            users = repo.list_users(**kwargs)
            display.display_user_list(users, long=args.long)
        except RepomanError, e:
            print e.message
            sys.exit(1)


class ListGroups(SubCommand):
    command = "list-groups"
    alias = 'lg'
    description = 'List user groups on the repoman repository.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('-l', '--long', action = 'store_true', default = False, help = 'Display extra information in a table.')
        self.get_arg_parser().add_argument('-a', '--all', action = 'store_true', default = False, help = 'Display all groups.')
        self.get_arg_parser().add_argument('-u', '--user', metavar = 'user', help = 'Display group membership for the given user.')
        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if args.all:
            kwargs = {'list_all':True}
        elif args.user:
            kwargs = {'user':args.user}
        else:
            kwargs = {}

        try:
            groups = repo.list_groups(**kwargs)
            display.display_group_list(groups, long=args.long)
        except RepomanError, e:
            print e.message
            sys.exit(1)




class ListImages(SubCommand):
    command_group = "advanced"
    command = 'list-images'
    alias = 'li'
    description = 'List a users images stored in the repository'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.formatter_class = argparse.RawDescriptionHelpFormatter
        p.add_argument('-a', '--all', action='store_true', default=False,
                       help="Display all images")
        p.add_argument('-l', '--long', action='store_true', default=False,
                       help='Display extra information for each image')
        p.add_argument('--sharedwith', action='store_true', default=False,
                       help='modifier flag.  See epilog for examples.')
        g = p.add_mutually_exclusive_group()
        g.add_argument('-u', '--user', help='List images owned by USER')
        g.add_argument('-g', '--group', help="List images shared with GROUP.")
        p.epilog = """\
Example Usages:

    repoman list
        list the current users images

    repoman list --sharedwith
        list all images shared with the current user

    repoman list --user bob
        list all images owned by the user 'bob'

    repoman list --sharedwith --user bob
        list all images shared with the user 'bob'

    repoman list --group babar
        list all images accessible by members of the 'babar' group

    repoman list --sharedwith --group babar
        has the same effect as the previous example."""

        return p

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('ListImages')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
    
        #TODO: impliment sharedwith calls
        repo = RepomanClient(config.host, config.port, config.proxy)
        if args.all:
            func = repo.list_all_images
            kwargs = {}
        elif args.group and not args.user:
            func = repo.list_images_shared_with_group
            kwargs = {'group':args.group}
        elif args.user and not args.group:
            if args.sharedwith:
                func = repo.list_images_shared_with_user
                kwargs = {'user':args.user}
            else:
                func = repo.list_user_images
                kwargs = {'user':args.user}
        else:
            if args.sharedwith:
                # shared with you
                func = repo.list_images_shared_with_user
                kwargs = {}
            else:
                func = repo.list_current_user_images
                kwargs = {}

        log.debug("function: '%s'" % func)
        log.debug("kwargs: '%s'" % kwargs)

        try:
            images = func(**kwargs)
            display.display_image_list(images, long=args.long)
        except RepomanError, e:
            print e.message
            sys.exit(1)


class List(ListImages):
    # Subclassed from ListImages because it's the same command.
    command_group = None
    command = "list"


