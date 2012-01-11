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
        self.get_arg_parser().set_defaults(func=self)

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
    command_group = 'advanced'
    command = 'remove-users-from-group'
    alias = 'rufg'
    description = 'Remove specifed users from group'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('group', help='group to add users to')
        p.add_argument('-u', '--users', nargs='+', metavar='USER', help='users to add')
        return p

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('RemoveUserFromGroup')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
        
        repo = RepomanClient(config.host, config.port, config.proxy)
        for user in args.users:
            status = "Removing user: `%s` from  group: '%s'\t\t" % (user, args.group)
            try:
                repo.remove_user_from_group(user, args.group)
                print '[OK]     %s' % status
            except RepomanError, e:
                print '[FAILED] %s\n\t-%s' % (status, e.message)

