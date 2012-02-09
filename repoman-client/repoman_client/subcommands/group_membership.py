from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.exceptions import RepomanError, SubcommandFailure
from repoman_client.config import config
import logging


class AddUserToGroup(SubCommand):
    command = 'add-users-to-group'
    alias = 'aug'
    description = 'Add specifed users to a group.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The group to add the specified user(s) to.')
        self.get_arg_parser().add_argument('users', metavar = 'user', nargs = '+', help = 'The user(s) to add to the group.')

    def __call__(self, args):
        for user in args.users:
            status = "Adding user: `%s` to group: '%s'\t\t" % (user, args.group)
            try:
                self.get_repoman_client(args).add_user_to_group(user, args.group)
                print '[OK]     %s' % status
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not add user: `%s` to group: '%s'" % (user, args.group), e)



class RemoveUserFromGroup(SubCommand):
    command = 'remove-users-from-group'
    alias = 'rug'
    description = 'Remove specifed users from a group.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The group to remove the specified user(s) from.')
        self.get_arg_parser().add_argument('users', metavar = 'user', nargs = '+', help = 'The user(s) to remove from the group.')

    def __call__(self, args):
        for user in args.users:
            status = "Removing user: `%s` from  group: '%s'\t\t" % (user, args.group)
            try:
                self.get_repoman_client(args).remove_user_from_group(user, args.group)
                print '[OK]     %s' % status
            except RepomanError, e:
                raise SubcommandFailure(self, "Could not remove user: `%s` from  group: '%s'" % (user, args.group), e)
