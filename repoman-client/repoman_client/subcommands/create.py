from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.logger import log
from repoman_client.subcommands.permissions import valid_permissions
import sys
import logging
import re

class CreateUser(SubCommand):
    command = "create-user"
    alias = 'cu'
    description = 'Create a new repoman user based on given information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('user', help = 'The name of the newly created user.  Must be unique and only contain characters ([a-Z][0-9][_][-]).')
        self.get_arg_parser().add_argument('full_name', help = 'The full name of the user.')
        self.get_arg_parser().add_argument('client_dn', help = 'The Distinguished Name (DN, looks like "/C=CA/O=Grid/OU=dept.org.ca/CN=John Doe")  of the certificate owned by the user and issued by a certificate authority, for example GridCanada.ca.')
        self.get_arg_parser().add_argument('email', help = 'The email address of the user.')

    def validate_args(self, args):
        if not re.match('^[a-zA-Z0-9_-]+$', args.user):
            log.info('Invalid username detected: %s' % (args.user))
            print 'Error: Invalid username.  Please see "repoman help %s" for acceptable username syntax.' % (self.command)
            sys.exit(1)
        if not re.match("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", args.email):
            log.info('Invalid user email address detected: %s' % (args.user))
            print 'Error: Invalid email address.  Please use a valid email address and try again.'
            sys.exit(1)

    def __call__(self, args):
        # Create user metadata arguments to pass to repoman server.
        kwargs = {}
        kwargs['user_name'] = args.user
        kwargs['cert_dn'] = args.client_dn
        kwargs['email'] = args.email
        kwargs['full_name'] = args.full_name

        try:
            self.get_repoman_client(args).create_user(**kwargs)
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
        self.get_arg_parser().add_argument('-p', '--permissions', metavar = 'list', nargs = '+', help = 'The permissions that the members of the group have (Blank separated list Ex: "user_delete image_modify").  Possible values are: %s.  See repoman manpage for a description of each permission.' % (', '.join(valid_permissions)))

    def validate_args(self, args):
        if not re.match('^[a-zA-Z0-9_-]+$', args.group):
            log.info('Invalid group name syntax detected: %s' % (args.group))
            print 'Error: Invalid group name syntax.  Please see "repoman help %s" for acceptable username syntax.' % (self.command)
            sys.exit(1)
        if args.permissions:
            for permission in args.permissions:
                if permission not in valid_permissions:
                    log.info('Invalid permission detected: %s' % (permission))
                    print 'Invalid permission: %s\nPlease chose one or more permission from the following list:\n[%s]' % (permission, ', '.join(valid_permissions))
                    sys.exit(1)

    def __call__(self, args):
        # Create group metadata arguments to pass to repoman server.
        kwargs = {}
        kwargs['name'] = args.group

        try:
            self.get_repoman_client(args).create_group(**kwargs)
            print "[OK]     Creating new group: '%s'" % (args.group)
        except RepomanError, e:
            print "[FAILED] Creating new group.\n\t-%s" % e
            sys.exit(1)

        # Add permissions to new group, if needed
        if args.permissions:
            for p in args.permissions:
                status = "Adding permission: '%s' to group: '%s'" % (p, args.group)
                try:
                    self.get_repoman_client(args).add_permission(args.group, p)
                    print "[OK]     %s" % status
                except RepomanError, e:
                    print "[FAILED] %s\n\t-%s" % (status, e)
                    sys.exit(1)

        # Add users to new group, if needed
        if args.users:
            for user in args.users:
                status = "Adding user: `%s` to group: '%s'\t\t" % (user, args.group)
                try:
                    self.get_repoman_client(args).add_user_to_group(user, args.group)
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
        self.get_arg_parser().add_argument('-a', '--unauthenticated_access', help = 'Defaults to False.  If set to true, the image may be retrieved by anybody who has the correct URL.', choices=['true', 'false'])
        self.get_arg_parser().add_argument('-d', '--description', metavar = 'value', help = 'Description of the image.')
        self.get_arg_parser().add_argument('-f', '--file', metavar = 'path', help = 'The path to the image file that will be uploaded to the repository.')
        self.get_arg_parser().add_argument('-h', '--hypervisor', metavar = 'value', help = 'The hypervisor.  Ex: xen, kvm, etc.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image.  The default is the ID of the current repoman user which can be determined with the command "repoman whoami" command.')
        self.get_arg_parser().add_argument('--os_arch', help = 'The operating system architecture.', choices = ['x86', 'x86_64'])
        self.get_arg_parser().add_argument('--os_type', metavar = 'value', help = 'The operating system type.  Ex: linux, unix, windows, etc.')
        self.get_arg_parser().add_argument('--os_variant', metavar = 'value', help = 'The operating system variant.  Ex: redhat, centos, ubuntu, etc.')


    def validate_args(self, args):
        if not re.match('^[a-zA-Z0-9_-]+$', args.image):
            log.info('Invalid image name syntax detected: %s' % (args.image))
            print 'Error: Invalid image name syntax.  Please see "repoman help %s" for acceptable image name syntax.' % (self.command)
            sys.exit(1)


    def __call__(self, args):
        try:
            # Create image metadata arguments to pass to repoman server.
            kwargs = {}
            kwargs['name'] = args.image
            if args.unauthenticated_access and args.unauthenticated_access.lower() == 'true':
                kwargs['unauthenticated_access'] = True
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

            self.get_repoman_client(args).create_image_metadata(**kwargs)
            print "[OK]     Created new image '%s'" % (kwargs['name'])
        except RepomanError, e:
            print "[FAILED] Creating new image '%s'\n\t-%s" % (kwargs['name'], e)
            sys.exit(1)

        if args.file:
            try:
                print "Uploading %s to new image '%s'..." % (args.file, kwargs['name'])
                self.get_repoman_client(args).upload_image(kwargs['name'], args.file)
                print "[OK]     %s uploaded to image '%s'" % (args.file, kwargs['name'])
            except RepomanError, e:
                print e
                sys.exit(1)
            except Exception:
                print "An unknown exception occured while uploading the image."
                sys.exit(1)

