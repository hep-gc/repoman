from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from argparse import ArgumentParser
import logging


class AddUserToGroup(SubCommand):
    command = 'add-users-to-group'
    alias = 'aug'
    description = 'Add specifed users to a group.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The name of the newly created group.  It must be unique and can only contain ([a-Z][0-9][_][-]) characters.')
        self.get_arg_parser().add_argument('users', metavar = 'user', nargs = '+', help = 'The user(s) to add to the group.')

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for user in args.users:
            status = "Adding user: `%s` to group: '%s'\t\t" % (user, args.group)
            try:
                repo.add_user_to_group(user, args.group)
                print '[OK]     %s' % status
            except RepomanError, e:
                print '[FAILED] %s\n\t-%s' % (status, e.message)



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
        repo = RepomanClient(config.host, config.port, config.proxy)
        for user in args.users:
            status = "Removing user: `%s` from  group: '%s'\t\t" % (user, args.group)
            try:
                repo.remove_user_from_group(user, args.group)
                print '[OK]     %s' % status
            except RepomanError, e:
                print '[FAILED] %s\n\t-%s' % (status, e.message)

