from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from argparse import ArgumentParser
import sys
import logging

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
        log = logging.getLogger('CreateUser')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
        
        repo = RepomanClient(config.host, config.port, config.proxy)
        if extra_args:
            try:
                kwargs = parse_unknown_args(extra_args)
            except ArgumentFormatError, e:
                print e.message
                sys.exit(1)
        else:
            kwargs={}
            
        log.debug("kwargs: '%s'" % kwargs)

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
        log = logging.getLogger('CreateGroup')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))

        repo = RepomanClient(config.host, config.port, config.proxy)
        if extra_args:
            try:
                kwargs = parse_unknown_args(extra_args)
            except ArgumentFormatError, e:
                print e.message
                sys.exit(1)
        else:
            kwargs={}

        log.debug("kwargs: '%s'" % kwargs)

        try:
            repo.create_group(**kwargs)
            print "[OK]     Creating new group."
        except RepomanError, e:
            print "[FAILED] Creating new group.\n\t-%s" % e
            sys.exit(1)



class CreateImage(SubCommand):
    command = "create-image"
    alias = 'ci'
    description = 'Create a new repoman image-slot based on the given information.  If an image file is supplied, then it will be uploaded to the repoman repository after the entry is created.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The name of the newly created image-slot on the repository.  This will be used to reference the image when running other repoman commands.  It must be unique within the owner\'s domain and can only contain ([a-Z][0-0][_][-]) characters.') 
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image.  The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')
        self.get_arg_parser().add_argument('-f', '--file', metavar = 'path', help = 'The path to the image file that will be uploaded to the repository.')
        self.get_arg_parser().add_argument('-d', '--description', metavar = 'value', help = 'Description of the image.')
        self.get_arg_parser().add_argument('--os_variant', metavar = 'value', help = 'The operating system variant.  Ex: redhat, centos, ubuntu, etc.')
        self.get_arg_parser().add_argument('--os_arch', help = 'The operating system architecture.', choices = ['x86', 'x86_64'])
        self.get_arg_parser().add_argument('--os_type', metavar = 'value', help = 'The operating system type.  Ex: linux, unix, windows, etc.')
        self.get_arg_parser().add_argument('--hypervisor', metavar = 'value', help = 'The hypervisor.  Ex: xen, kvm, etc.')
        self.get_arg_parser().add_argument('-a', '--unauthenticated_access', help = 'Defaults to False.  If set to True, the image may be retrieved by anybody who has the correct URL.', choices=['True', 'False'])

        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)

        try:
            # Create image metadata arguments to pass to repoman server.
            kwargs = {}
            kwargs['name'] = args.image
            if args.unauthenticated_access:
                kwargs['unauthenticated_access'] = args.unauthenticated_access
            if args.description:
                kwargs['description'] = args.description
            if args.hypervisor:
                kwargs['hypervisor'] = args.hypervisor
            if args.owner:
                kwargs['owner'] = args.owner
            if args.os_arch:
                kwargs['os_arch'] = args.os_arch
            if args.os_type:
                kwargs['os_type'] = args.os_type
            if args.os_variant:
                kwargs['os_variant'] = args.os_variant

            repo.create_image_metadata(**kwargs)
            print "[OK]     Created new image meatadata."
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

