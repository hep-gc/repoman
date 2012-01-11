from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from argparse import ArgumentParser
import sys
import logging

class CreateUser(SubCommand):
    command = "create-user"
    alias = 'cu'
    description = 'Create a new repoman user based on given information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('user', help = 'The name of the newly created user.  Must be unique and only contain characters ([a-Z][0-0][_][-]).')
        self.get_arg_parser().add_argument('client_dn', help = 'The Distinguished Name (DN, looks like "/C=CA/O=Grid/OU=dept.org.ca/CN=John Doe")  of the certificate owned by the user and issued by a certificate authority, for example GridCanada.ca.')
        self.get_arg_parser().add_argument('-e', '--email', metavar = 'address', help = 'The email address of the user.')
        self.get_arg_parser().add_argument('-f', '--full_name', metavar = 'name', help = 'The full name of the user.')

        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)

        # Create user metadata arguments to pass to repoman server.
        kwargs = {}
        kwargs['user_name'] = args.user
        kwargs['client_dn'] = args.client_dn
        if args.email:
            kwargs['email'] = args.email
        if args.full_name:
            kwargs['full_name'] = args.full_name

        try:
            repo.create_user(**kwargs)
            print "[OK]     Created new user %s." % (args.user)
        except RepomanError, e:
            print "[FAILED] Creating new user.\n\t-%s" % e
            sys.exit(1)



class CreateGroup(SubCommand):
    command = "create-group"
    alias = 'cg'
    description = 'Create a new group based on given information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('group', help = 'The name of the newly created group. It must be unique and can only contain characters ([a-Z][0-0][_][-]).')
        self.get_arg_parser().add_argument('-u', '--users', metavar = 'list', nargs='+', help = 'The users that are members of the group. (Blank separated list) Ex: "msmithsjobs"')
        self.get_arg_parser().add_argument('-p', '--permissions', metavar = 'list', nargs = '+', help = 'The permissions that the members of the group have (Blank separated list Ex: "user_delete image_modify").  Possible values are: group_create, group_delete, group_modify, group_modify_membership, group_modify_permissions, image_create, image_delete, image_delete_group, image_modify, image_modify_group, user_create, user_delete, user_modify, user_modify_self.  See repoman manpage for a description of each permission.')
        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)

        # Create group metadata arguments to pass to repoman server.
        kwargs = {}
        kwargs['name'] = args.group

        try:
            repo.create_group(**kwargs)
            print "[OK]     Creating new group: '%s'" % (args.group)
        except RepomanError, e:
            print "[FAILED] Creating new group.\n\t-%s" % e
            sys.exit(1)

        # Add permissions to new group, if needed
        if args.permissions:
            for p in args.permissions:
                status = "Adding permission: '%s' to group: '%s'" % (p, args.group)
                try:
                    repo.add_permission(args.group, p)
                    print "[OK]     %s" % status
                except RepomanError, e:
                    print "[FAILED] %s\n\t-%s" % (status, e)
                    sys.exit(1)

        # Add users to new group, if needed
        if args.users:
            for user in args.users:
                status = "Adding user: `%s` to group: '%s'\t\t" % (user, args.group)
                try:
                    repo.add_user_to_group(user, args.group)
                    print '[OK]     %s' % status
                except RepomanError, e:
                    print '[FAILED] %s\n\t-%s' % (status, e.message)


        
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

