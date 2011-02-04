from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError
from argparse import ArgumentParser
import sys

class CreateUser(SubCommand):
    command_group = "advanced"
    command = "create-user"
    alias = 'cu'
    description = 'Create a new user account based on given information'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "create-user [-h] [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
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
            repo.create_user(**kwargs)
            print "[OK]     Creating new user."
        except RepomanError, e:
            print "[FAILED] Creating new user.\n\t-%s" % e
            sys.exit(1)



class CreateGroup(SubCommand):
    command_group = "advanced"
    command = "create-group"
    alias = 'cg'
    description = 'Create a new group based on given information'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "create-group [-h] [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
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
            repo.create_group(**kwargs)
            print "[OK]     Creating new group."
        except RepomanError, e:
            print "[FAILED] Creating new group.\n\t-%s" % e
            sys.exit(1)



class CreateImage(SubCommand):
    command_group = "advanced"
    command = "create-image"
    alias = 'ci'
    description = 'Create a new image based on given information'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "create-image [-h] [-f FILE] [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
        p.add_argument('-f', '--file', help='Image file to upload')
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

        if args.file and not kwargs.get('name'):
            name = args.file.rsplit('/', 1)[-1]
            kwargs.update({'name':name})

        try:
            repo.create_image_metadata(**kwargs)
            print "[OK]     Creating new image meatadata."
        except RepomanError, e:
            print "[FAILED] Creating new image metadata.\n\t-%s" % e
            sys.exit(1)

        if args.file:
            try:
                repo.upload_image(kwargs['name'], args.file)
            except RepomanError, e:
                print e
                sys.exit(1)
            except Exception:
                print "An unknown exception occured while uploading the image."
                sys.exit(1)

