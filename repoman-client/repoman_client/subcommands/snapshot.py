from repoman_client.subcommand import SubCommand
from argparse import ArgumentParser
import sys

class SnapshotSystem(SubCommand):
    command_group = 'advanced'
    command = 'snapshot-system'
    alias = None
    description = 'Snapshots currently running system'

    def get_parser(self):
        p = ArgumentParser(description)
        padd_argument('-u', '--upload', action='store_true', default=False,
                      help='Upload to repository after snapshot')
        p.add_argument('-f', '--force', action='store_true', default=False,
                       help='Force overwriting an existing image')
        return p

    def __call__(self, args, extra_args=None):
        pass

