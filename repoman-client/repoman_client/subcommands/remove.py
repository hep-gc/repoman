from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
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
        repo = RepomanClient(config.host, config.port, config.proxy)
        if not args.force:
            print ("WARNING:\n"
                    "\tAll images owned by the user will be removed.\n"
                    "\tThis operation cannot be undone!")
            if not yes_or_no():
                print "Aborting user deletion"
                return
        try:
            repo.remove_user(args.user)
            print "[OK]     Removed user %s." % (args.user)
        except RepomanError, e:
            print "[FAILED] Removing user.\n\t-%s" % e
            sys.exit(1)




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
        repo = RepomanClient(config.host, config.port, config.proxy)
        if not args.force:
            if not yes_or_no():
                print "Aborting group deletion"
                return

        try:
            repo.remove_group(args.group)
            print "[OK]     Removed group %s." % (args.group)
        except RepomanError, e:
            print "[FAILED] Removing group.\n\t-%s" % e
            sys.exit(1)


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

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if not args.force:
            print ("WARNING:\n"
                    "\tdeleting an image cannot be undone.\n")
            if not yes_or_no():
                print "Aborting user deletion"
                return

        try:
            repo.remove_image(args.image)
            print "[OK]     Removed image %s." % (args.image)
        except RepomanError, e:
            print "[FAILED] Removing image.\n\t-%s" % e
            sys.exit(1)



