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


    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if args.group:
            kwargs = {'group':args.group}
        else:
            kwargs = {}
            
        try:
            users = repo.list_users(**kwargs)
            display.display_user_list(users, long_output=args.long)
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
            display.display_group_list(groups, long_output=args.long)
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
        g1.add_argument('-g', '--group', metavar = 'group', help = 'List all images shared between you and the named group.')
        g1.add_argument('-u', '--user', metavar = 'user', help = 'List all images shared between you and the named user.')
        g2 = self.get_arg_parser().add_mutually_exclusive_group()
        g2.add_argument('-l', '--long',  action = 'store_true', default = False, help = 'List images, together with additional information, in a table.')
        g2.add_argument('-U', '--url', action = 'store_true', default = False, help = 'List images and associated URLs.')


    def __call__(self, args):
        #
        # TODO: We need to implement some smarter server-side image listing
        # commands and then cleanup this method to use these new functions.
        # (Andre)
        #
        images = []
        repo = RepomanClient(config.host, config.port, config.proxy)
        if args.all:
            # List images that the user has access to.
            # (either via ownership, or shared by user or group membership.)
            # For a repoman admin, this will be all images on the server.
            #func = repo.list_all_images
            kwargs = {}
            images = repo.list_current_user_images(**kwargs)
            images += repo.list_images_shared_with_user(**kwargs)           
        elif args.group:
            # List images accessible by you and by members of the named group.
            # First check if the user is a member of the group.  If not, then
            # return an empty list.
            kwargs = {'group':args.group}
            groups = repo.whoami()['groups']
            for group in groups:
                if group.split('/')[-1] == args.group:
                    images = repo.list_images_shared_with_group(**kwargs)
        elif args.user:
            current_user = repo.whoami()['user_name']
            # List all current user's images shared with the given user, AND all of the
            # given user's images shared with the current user.
            kwargs = {'user':args.user}
            all_images_shared_with_given_user = repo.list_images_shared_with_user(**kwargs)
            for image in all_images_shared_with_given_user:
                if image.split('/')[-2] == current_user:
                    images.append(image)

            kwargs = {'user':current_user}
            all_images_shared_with_me = repo.list_images_shared_with_user(**kwargs)
            for image in all_images_shared_with_me:
                if image.split('/')[-2] == args.user:
                    images.append(image)

        else:
            # List only images owned by current user.
            kwargs = {}
            images = repo.list_current_user_images(**kwargs)

        try:
            # Get the metadata of each image.
            # TODO: This is a non-efficient hack that will be cleaned-up later. (Andre)
            images_metadata = []
            for image in images:
                name = image.rsplit('/', 2)
                images_metadata.append(repo.describe_image("%s/%s" % (name[-2], name[-1])))
            display.display_image_list(images_metadata, long_output=args.long, urls=args.url)
        except RepomanError, e:
            print e.message
            sys.exit(1)



