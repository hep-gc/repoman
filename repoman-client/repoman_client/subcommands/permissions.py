from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.exceptions import RepomanError, SubcommandFailure
from repoman_client.config import config
from repoman_client.subcommand import SubCommand
import logging

# This is a list of valid permissions.
# Use it to validate arguments, or to print out in help messages.
# NOTE: Do not forget to edit this list if the list of permissions changes.
valid_permissions = ['group_create', 'group_delete',  'group_modify',   'group_modify_membership',   'group_modify_permissions',   'image_create',   'image_delete',  'image_delete_group', 'image_modify', 'image_modify_group', 'user_create', 'user_delete', 'user_modify', 'user_modify_self']

class AddPermission(SubCommand):
    command = 'add-permissions-to-group'
    alias = 'apg'
    description = 'Add specified permissions to a group.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The group that you are adding permissions to. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('permissions', help = 'Comma separated list of the permissions to add to the group. Possible values are: %s. See the repoman manpage for a description of each permission.' % (', '.join(valid_permissions)))


    def __call__(self, args):
        for p in args.permissions.split(','):
            status = "Adding permission: '%s' to group: '%s'" % (p, args.group)
            try:
                self.get_repoman_client(args).add_permission(args.group, p)
                print "[OK]     %s" % status
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not add permission: '%s' to group: '%s'" % (p, args.group), e)


class RemovePermission(SubCommand):
    command = 'remove-permissions-from-group'
    alias = 'rpg'
    description = 'Remove specified permission(s) from a group.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The group that you are removing permissions from. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('permissions', help = 'Comma separated list of the  permissions to remove from the group.  Use the "repoman describe-group" command to see possible values for a particular group.')

    def __call__(self, args):
        for p in args.permissions.split(','):
            status = "Removing permission: '%s' from group: '%s'" % (p, args.group)
            try:
                self.get_repoman_client(args).remove_permission(args.group, p)
                print "[OK]     %s" % status
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not remove permission: '%s' from group: '%s'" % (p, args.group), e)
