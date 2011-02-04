from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from argparse import ArgumentParser


class AddUserToGroup(SubCommand):
    command_group = 'advanced'
    command = 'add-users-to-group'
    alias = 'autg'
    description = 'Add make specifed users members of a group'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('group', help='group to add users to')
        p.add_argument('-u', '--users', nargs='+', metavar='USER', help='users to add')
        return p

    def __call__(self, args, extra_args=None):
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
        repo = RepomanClient(config.host, config.port, config.proxy)
        for user in args.users:
            status = "Removing user: `%s` from  group: '%s'\t\t" % (user, args.group)
            try:
                repo.remove_user_from_group(user, args.group)
                print '[OK]     %s' % status
            except RepomanError, e:
                print '[FAILED] %s\n\t-%s' % (status, e.message)

