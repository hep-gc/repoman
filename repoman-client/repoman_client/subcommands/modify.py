from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError
from argparse import ArgumentParser
import sys

class ModifyUser(SubCommand):
    command_group = "advanced"
    command = "modify-user"
    alias = 'mu'
    description = 'Modify an existing user with the given information'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "modify-user [-h] user [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
        p.add_argument('user', help='The existing user you want to modify')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if extra_args:
            try:
                kwargs = parse_unknown_args(extra_args)
            except ArgumentFormatError, e:
                print e.message
                sys.exit(1)
        else:
            kwargs={}

        try:
            repo.modify_user(args.user, **kwargs)
            print "[OK]     Modifying user."
        except RepomanError, e:
            print "[FAILED] Modifying user.\n\t-%s" % e
            sys.exit(1)



class ModifyGroup(SubCommand):
    command_group = "advanced"
    command = "modify-group"
    alias = 'mg'
    description = 'Modify an existing group with the given information'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "modify-group [-h] group [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
        p.add_argument('group', help='The existing group you want to modify')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if extra_args:
            try:
                kwargs = parse_unknown_args(extra_args)
            except ArgumentFormatError, e:
                print e.message
                sys.exit(1)
        else:
            kwargs={}

        try:
            repo.modify_group(args.group, **kwargs)
            print "[OK]     Modifying group."
        except RepomanError, e:
            print "[FAILED] Modifying group.\n\t-%s" % e
            sys.exit(1)



class ModifyImage(SubCommand):
    command_group = "advanced"
    command = "modify-image"
    alias = 'mi'
    description = 'Modify an existing image with the given information'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "modify-image [-h] image [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
        p.add_argument('image', help='The existing image you want to modify')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if extra_args:
            try:
                kwargs = parse_unknown_args(extra_args)
            except ArgumentFormatError, e:
                print e.message
                sys.exit(1)
        else:
            kwargs={}

        try:
            repo.modify_image(args.image, **kwargs)
            print "[OK]     Modifying image."
        except RepomanError, e:
            print "[FAILED] Modifying image.\n\t-%s" % e
            sys.exit(1)



class Rename(SubCommand):
    command = 'rename'
    alias = 'rn'
    description = "rename an existing image from 'old' to 'new'"

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('old', help='name of exiting image')
        p.add_argument('new', help='new name that existing image will get')
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)

        kwargs = {'name':args.new}
        try:
            repo.modify_image(args.old, **kwargs)
            print "[OK]     Renaming image."
        except RepomanError, e:
            print "[FAILED] Renaming image.\n\t-%s" % e
            sys.exit(1)

