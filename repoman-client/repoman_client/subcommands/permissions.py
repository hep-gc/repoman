from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.subcommand import SubCommand
from argparse import ArgumentParser

class AddPermission(SubCommand):
    command_group = 'advanced'
    command = 'add-permissions'
    alias = 'ap'
    description = 'Add permissions to groups'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('group', help='group to add permissions to')
        p.add_argument('-p', '--permissions', nargs='+', metavar='PERMISSION',
                       help='List of permissions to add')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for p in args.permissions:
            status = "Adding permission: '%s' to group: '%s'" % (p, args.group)
            try:
                repo.add_permission(args.group, p)
                print "[OK]     %s" % status
            except RepomanError, e:
                print "[FAILED] %s\n\t-%s" % (status, e)


class RemovePermission(SubCommand):
    command_group = 'advanced'
    command = 'remove-permissions'
    alias = 'rp'
    description = 'Remove specified permissions from group'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('group', help='group to remove permissions from')
        p.add_argument('-p', '--permissions', nargs='+', metavar='PERMISSION',
                       help='List of permissions to remove')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        for p in args.permissions:
            status = "Removing permission: '%s' from group: '%s'" % (p, args.group)
            try:
                repo.remove_permission(args.group, p)
                print "[OK]     %s" % status
            except RepomanError, e:
                print "[FAILED] %s\n\t-%s" % (status, e)

