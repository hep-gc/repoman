from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.exceptions import RepomanError, SubcommandFailure
from repoman_client.config import config
from repoman_client import display
from repoman_client.logger import log
import argparse
import sys

class ListUsers(SubCommand):
    command = "list-users"
    alias = 'lu'
    description = 'List repoman users.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        group = self.get_arg_parser().add_mutually_exclusive_group()
        group.add_argument('-s', '--short', action = 'store_true', default = False, help = 'List users with no additional information.')
        self.get_arg_parser().add_argument('-g', '--group', metavar = 'group', help = 'Only display users that belong to the given group.')
        self.get_arg_parser().add_argument('user', metavar = 'user', nargs = '?', help = 'If given, information about this user only will be displayed.')
        


    def __call__(self, args):
        try:
            users = []
            full_output = False
            if args.user:
                users.append(self.get_repoman_client(args).describe_user(args.user))
                full_output = True
            else:
                users_urls = self.get_repoman_client(args).list_users(group = args.group)
                # Fetch metadata for each user.
                # TODO: Create a server method that will return the metadata
                # of all users and use that instead. (Andre)
                for user_url in users_urls:
                    users.append(self.get_repoman_client(args).describe_user(user_url.rsplit('/',1)[-1]))

            display.display_user_list(users, short_output=args.short, full_output=full_output)
        except RepomanError, e:
            raise SubcommandFailure(self, 'Error listing user(s).', e)


class ListGroups(SubCommand):
    command = "list-groups"
    alias = 'lg'
    short_description = 'List user groups on the repoman repository.'
    description = 'List user groups on the repoman repository.  By default, this command will only list groups that you belong to.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        group = self.get_arg_parser().add_mutually_exclusive_group()
        group.add_argument('-s', '--short', action = 'store_true', default = False, help = 'List groups with no additional information.')
        group2 = self.get_arg_parser().add_mutually_exclusive_group()
        group2.add_argument('-a', '--all', action = 'store_true', default = False, help = 'Display all groups.')
        group2.add_argument('-u', '--user', metavar = 'user', help = 'Display group membership for the given user.')
        group2.add_argument('group', nargs = '?', help = 'If given, information about this group only will be displayed.')

    def __call__(self, args):
        if args.all:
            kwargs = {'list_all':True}
        elif args.user:
            kwargs = {'user':args.user}
        else:
            kwargs = {}

        groups = []
        full_output = False

        try:
            if args.group:
                groups.append(self.get_repoman_client(args).describe_group(args.group))
                full_output = True
            else:
                groups_urls = self.get_repoman_client(args).list_groups(**kwargs)
                # Fetch metadata for each group.
                # TODO: Create a server method that will return the metadata
                # of all groups and use that instead. (Andre)
                for group_url in groups_urls:
                    groups.append(self.get_repoman_client(args).describe_group(group_url.rsplit('/',1)[-1]))

            display.display_group_list(groups, short_output=args.short, full_output=full_output)
        except RepomanError, e:
            raise SubcommandFailure(self, 'Error listing group(s).', e)




class ListImages(SubCommand):
    command = 'list-images'
    alias = 'li'
    description = 'List images stored in the repository.  By default, only images owned by the current user are listed.'
    # We need to override the usage else argparse will not format the second
    # mutually exclusive group correctly. (bug in argparse?)
    usage = '%(prog)s [-o owner] [-s | -U] [-a | -g group | -u user | image]'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        # This argument should be on its own, outside of the 2 mutually exclusive groups
        # defined below.
        # Note that adding this argument causes the second mutually exclusive
        # group to be broken up. Bug in argparse?  Maybe...
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'owner', help='The owner of the given image.  The default is the ID of the current repoman user which can be determined with the "repoman whoami" command.  This option is only used if an image is given as argument.')

        # First mutually exclusive group
        group = self.get_arg_parser().add_mutually_exclusive_group()
        group.add_argument('-s', '--short',  action = 'store_true', default = False, help = 'List images with no additional information.')
        group.add_argument('-U', '--url', action = 'store_true', default = False, help = 'List images and associated URLs.')

        # Second mutually exclusive group
        group2 = self.get_arg_parser().add_mutually_exclusive_group()
        group2.add_argument('-a', '--all', action = 'store_true', default = False, help = 'List all images accessible by you.')
        group2.add_argument('-g', '--group', metavar = 'group', help = 'List all images shared between you and the named group.')
        group2.add_argument('-u', '--user', metavar = 'user', help = 'List all images shared between you and the named user.')
        group2.add_argument('image', nargs = '?', help = 'If given, information about this image only will be displayed.')


    def __call__(self, args):
        #
        # TODO: We need to implement some smarter server-side image listing
        # commands and then cleanup this method to use these new functions.
        # (Andre)
        #
        images = []
        images_metadata = []
        full_output = False

        try:
            if args.image:
                image_name = args.image
                full_output = True
                if args.owner:
                    image_name = "%s/%s" % (args.owner, args.image)
                log.debug('Fetching info of single image "%s"' % (image_name))
                images_metadata.append(self.get_repoman_client(args).describe_image(image_name))
            else:
                if args.all:
                    # List images that the user has access to.
                    # (either via ownership, or shared by user or group membership.)
                    # For a repoman admin, this will be all images on the server.
                    #func = repo.list_all_images
                    log.debug('Listing all images...')
                    kwargs = {}
                    images = self.get_repoman_client(args).list_current_user_images(**kwargs)
                    images += self.get_repoman_client(args).list_images_shared_with_user(**kwargs)
                elif args.group:
                    # List images accessible by you and by members of the named group.
                    # First check if the user is a member of the group.  If not, then
                    # return an empty list.
                    log.debug('Listing all images for group "%s"' % (args.group))
                    kwargs = {'group':args.group}
                    groups = self.get_repoman_client(args).whoami()['groups']
                    for group in groups:
                        if group.split('/')[-1] == args.group:
                            images = self.get_repoman_client(args).list_images_shared_with_group(**kwargs)
                elif args.user:
                    log.debug('Listing all current user\'s images shared with user %s' % (args.user))
                    current_user = self.get_repoman_client(args).whoami()['user_name']
                    # List all current user's images shared with the given user, AND all of the
                    # given user's images shared with the current user.
                    kwargs = {'user':args.user}
                    all_images_shared_with_given_user = self.get_repoman_client(args).list_images_shared_with_user(**kwargs)
                    for image in all_images_shared_with_given_user:
                        if image.split('/')[-2] == current_user:
                            images.append(image)

                    kwargs = {'user':current_user}
                    all_images_shared_with_me = self.get_repoman_client(args).list_images_shared_with_user(**kwargs)
                    for image in all_images_shared_with_me:
                        if image.split('/')[-2] == args.user:
                            images.append(image)

                else:
                    # List only images owned by current user.
                    log.debug('Listing images owned by current user.')
                    kwargs = {}
                    images = self.get_repoman_client(args).list_current_user_images(**kwargs)

                # Get the metadata of each image.
                # TODO: This is a non-efficient hack that will be cleaned-up later. (Andre)
                log.debug('Images:\n%s\n' % (images))
                for image in images:
                    try:
                        name = image.rsplit('/', 2)
                        log.debug('Fetching image metadata for "%s" [%s]' % (image, name))
                        images_metadata.append(self.get_repoman_client(args).describe_image("%s/%s" % (name[-2], name[-1])))
                    except RepomanError, e:
                        print "Warning: Error in retreiving information about image '%s'.  Skipping..." % (image)
                    except Exception, e:
                        raise RepomanError(self, "Error in retreiving information about image '%s'." % (image), e)

        except RepomanError, e:
            raise SubcommandFailure(self, 'Error listing image(s).', e)

        # Remove duplicates first
        images_metadata_dedup = []
        for i in images_metadata:
            if i not in images_metadata_dedup:
                images_metadata_dedup.append(i)

        display.display_image_list(images_metadata_dedup, short_output=args.short, full_output=full_output, urls=args.url)



