from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.subcommand import SubCommand
from argparse import ArgumentParser
import logging


class AddPermission(SubCommand):
    command = 'add-permissions-to-group'
    alias = 'apg'
    description = 'Add specified permissions to a group.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The group that you are adding permissions to. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('permission', nargs = '+', help = 'The permission(s) to add to the group. Possible values are: group_create, group_delete,  group_modify,   group_modify_membership,   group_modify_permissions,   image_create,   image_delete,  image_delete_group, image_modify, image_modify_group, user_create, user_delete, user_modify, user_modify_self. See the repoman manpage for a description of each permission.')


    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for p in args.permission:
            status = "Adding permission: '%s' to group: '%s'" % (p, args.group)
            try:
                repo.add_permission(args.group, p)
                print "[OK]     %s" % status
            except RepomanError, e:
                print "[FAILED] %s\n\t-%s" % (status, e)


class RemovePermission(SubCommand):
    command = 'remove-permissions-from-group'
    alias = 'rpg'
    description = 'Remove specified permission(s) from a group.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The group that you are removing permissions from. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('permission', nargs = '+', help = 'The  permission(s)  to  remove  from  the  group.  Possible values are: group_create, group_delete, group_modify, group_modify_membership, group_modify_permissions, image_create, image_delete, image_delete_group, image_modify, image_modify_group, user_create, user_delete, user_modify, user_modify_self. See the repoman manpage for a description of each permission.')

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for p in args.permission:
            status = "Removing permission: '%s' from group: '%s'" % (p, args.group)
            try:
                repo.remove_permission(args.group, p)
                print "[OK]     %s" % status
            except RepomanError, e:
                print "[FAILED] %s\n\t-%s" % (status, e)

