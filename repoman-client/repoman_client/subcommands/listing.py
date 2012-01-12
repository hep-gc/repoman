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
    command = 'list-images'
    alias = 'li'
    description = 'List images stored in the repository.  By default, only images owned by the current user are listed.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        g1 = self.get_arg_parser().add_mutually_exclusive_group()
        g1.add_argument('-a', '--all', action = 'store_true', default = False, help = 'List all images accessible by you.')
        g1.add_argument('-g', '--group', metavar = 'group', help = 'List images accessible by you and by members of the named group.')
        g1.add_argument('-u', '--user', metavar = 'user', help = 'List all images shared between you and the named user.')
        g2 = self.get_arg_parser().add_mutually_exclusive_group()
        g2.add_argument('-l', '--long',  action = 'store_true', default = False, help = 'Display a table with extra information.')
        g2.add_argument('-U', '--url', action = 'store_true', default = False, help = 'In addition to the name, display the HTTP and HTTPS URLs of each image.')
        self.get_arg_parser().set_defaults(func=self)


    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if args.all:
            func = repo.list_all_images
            kwargs = {}
        elif args.group:
            func = repo.list_images_shared_with_group
            kwargs = {'group':args.group}
        elif args.user:
            func = repo.list_user_images
            kwargs = {'user':args.user}
        elif args.sharedwith != None and args.sharedwith == '':
            func = repo.list_images_shared_with_user
            kwargs = {}
        elif args.sharedwith and args.sharedwith != '':
            func = repo.list_images_shared_with_user
            kwargs = {'user':args.sharedwith}
        else:
            func = repo.list_current_user_images
            kwargs = {}

        try:
            images = func(**kwargs)
            display.display_image_list(images, long=args.long)
        except RepomanError, e:
            print e.message
            sys.exit(1)



