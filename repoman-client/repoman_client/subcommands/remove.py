from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.exceptions import RepomanError, SubcommandFailure
from repoman_client.config import config
from repoman_client.utils import yes_or_no
import sys
import logging


class RemoveUser(SubCommand):
    command = "remove-user"
    alias = 'ru'
    description = 'Remove a repoman user. Note: All images owned by user will be deleted.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('user', help='The user to delete. Use "repoman list-users" to see possible values.')
        self.get_arg_parser().add_argument('-f', '--force', action='store_true', default=False,
                       help='Delete user without confirmation.')


    def __call__(self, args):
        if not args.force:
            print ("WARNING:\n"
                    "\tAll images owned by the user will be removed.\n"
                    "\tThis operation cannot be undone!")
            if not yes_or_no():
                print "Aborting user deletion"
                return
        try:
            self.get_repoman_client(args).remove_user(args.user)
            print "[OK]     Removed user %s." % (args.user)
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not remove user '%s'" % (args.user), e)



class RemoveGroup(SubCommand):
    command = "remove-group"
    alias = 'rg'
    description = 'Remove a group from the repoman repository.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help='The group to delete.')
        self.get_arg_parser().add_argument('-f', '--force', action='store_true', default=False,
                       help='Delete group without confirmation.')

    def __call__(self, args):
        if not args.force:
            if not yes_or_no():
                print "Aborting group deletion"
                return

        try:
            self.get_repoman_client(args).remove_group(args.group)
            print "[OK]     Removed group %s." % (args.group)
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not remove group '%s'" % (args.group), e)



class RemoveImage(SubCommand):
    command = 'remove-image'
    alias = 'ri'
    description = 'Delete the specified image from the repository.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help='The name of the image to be deleted.')
        self.get_arg_parser().add_argument('-f', '--force', action='store_true', default=False,
                       help='Delete image without confirmation.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image.  The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')

    def __call__(self, args):
        if not args.force:
            print ("WARNING:\n"
                    "\tdeleting an image cannot be undone.\n")
            if not yes_or_no():
                print "Aborting user deletion"
                return

        image_name = args.image
        if args.owner:
            image_name = '%s/%s' % (args.owner, args.image
)
        try:
            self.get_repoman_client(args).remove_image(image_name)
            print "[OK]     Removed image %s." % (args.image)
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not remove image '%s'" % (args.image), e)
