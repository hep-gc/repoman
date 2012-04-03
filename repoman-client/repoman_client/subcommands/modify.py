from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.exceptions import RepomanError, InvalidArgumentError, SubcommandFailure
from repoman_client.config import config
from repoman_client.subcommands.permissions import valid_permissions
from repoman_client.logger import log
import sys
import logging
import re

class ModifyUser(SubCommand):
    command = "modify-user"
    alias = 'mu'
    description = 'Modify a repoman user with the given metadata information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('user', help = 'The name of the user to be modified.  See "repoman list-users" to see possible values.')
        self.get_arg_parser().add_argument('-c', '--client_dn', metavar = 'dn', help = 'The Distinguised Name (DN) of the certificate which is owned by the user.')
        self.get_arg_parser().add_argument('-e', '--email', metavar = 'address', help = 'The email address of the user.')
        self.get_arg_parser().add_argument('-f', '--full_name', metavar = 'name', help = 'The full name of the user.')
        self.get_arg_parser().add_argument('-n', '--new_name', metavar = 'user', help = 'The new unique username for the user.')


    def validate_args(self, args):
        if args.new_name:
            # Temporary error message until renaming a user gets implemented (or feature removed).
            raise InvalidArgumentError('Sorry, this version of the repoman client does not support renaming an existing user.')
        if args.new_name and not re.match(config.get_image_name_regex(), args.new_name):
            raise InvalidArgumentError('Invalid new username.  Please see "repoman help %s" for acceptable username syntax.' % (self.command))
        if args.email and not re.match("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", args.email):
            raise InvalidArgumentError('Invalid email address.  Please use a valid email address and try again.')


    def __call__(self, args):
        kwargs = {}
        if args.full_name:
            kwargs['full_name'] = args.full_name
        if args.email:
            kwargs['email'] = args.email
        if args.new_name:
            kwargs['user_name'] = args.new_name
        if args.client_dn:
            kwargs['cert_dn'] = args.client_dn

        try:
            self.get_repoman_client(args).modify_user(args.user, **kwargs)
            print "[OK]     Modifying user."
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not modify user '%s'" % (args.user), e)



class ModifyGroup(SubCommand):
    command = "modify-group"
    alias = 'mg'
    description = 'Modify a group with the given information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        # Subcommand: modify-group
        self.get_arg_parser().add_argument('group', help = 'The group you want to modify. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('-n', '--new_name', metavar = 'value', help = 'The name of the group.  It must be unique and can only contain ([a-Z][0-9][_][-]) characters.')
        self.get_arg_parser().add_argument('-p', '--permissions', metavar = 'permissions', help = 'The permissions that the members of the group have (Comma separated list  Ex: user_delete,image_modify).  Possible values are: %s.  See repoman manpage description of each permission.' % (','.join(valid_permissions)))
        self.get_arg_parser().add_argument('-u', '--users', metavar = 'users', help = 'The users that are members of the group.  (Comma separated list) Ex: msmith,sjobs')

        
    def validate_args(self, args):
        if args.new_name and not re.match('^[a-zA-Z0-9_-]+$', args.new_name):
            raise InvalidArgumentError('Invalid group name syntax.  Please see "repoman help %s" for acceptable username syntax.' % (self.command))
        if args.permissions:
            for permission in args.permissions.split(','):
                if permission not in valid_permissions:
                    log.info('Invalid permission detected: %s' % (permission))
                    raise InvalidArgumentError('Invalid permission: %s\nPlease chose one or more permission from the following list:\n[%s]' % (permission, ', '.join(valid_permissions)))


    def __call__(self, args):
        kwargs={}
        if args.new_name:
            kwargs['name'] = args.new_name
        if args.permissions:
            kwargs['permissions'] = args.permissions.split(',')
        if args.users:
            kwargs['users'] = args.users.split(',')

        try:
            self.get_repoman_client(args).modify_group(args.group, **kwargs)
            print "[OK]     Modifying group."
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not modify group '%s'" % (args.group), e)



class ModifyImage(SubCommand):
    command = "modify-image"
    alias = 'mi'
    description = 'Modify an image with the given information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The name of the image to modify. Use "repoman list-images" to see possible values.') 
        self.get_arg_parser().add_argument('-a', '--unauthenticated_access', choices=['true', 'false'], help = 'Defaults  to  false.  If  set  to  true, the image may be retrieved by anybody who has the correct URL.')
        self.get_arg_parser().add_argument('-d', '--description', metavar = 'value', help = 'Description of the image.')
        self.get_arg_parser().add_argument('-h', '--hypervisor', metavar = 'value', help = 'The hypervisor. Ex: xen, kvm, etc.')
        self.get_arg_parser().add_argument('-n', '--new_name', metavar = 'value', help = 'The new name of the image-slot on the repository.  This  will be used to reference the image when running other repoman commands. It must be unique  to  the  owner\'s domain and can only contain ([a-Z][0-9][_][-][.]) characters.') 
        self.get_arg_parser().add_argument('-N', '--new_owner', metavar = 'user', help = 'The new owner of the named image. Use "repoman list-users" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can be determined with the "repoman whoami" command.')
        self.get_arg_parser().add_argument('--os_arch', choices = ['x86', 'x86_64'], help = 'The  operating  system  architecture.')
        self.get_arg_parser().add_argument('--os_type', metavar = 'value', help = 'The operating system type.  Ex:  linux,  unix, windows, etc.')
        self.get_arg_parser().add_argument('--os_variant', metavar = 'value', help = 'The operating system variant. Ex: redhat, centos, ubuntu, etc.')


    def validate_args(self, args):
        if args.new_name and not re.match(config.get_image_name_regex(), args.new_name):
            raise InvalidArgumentError('Image name parameter contains invalid characters. Use only alphanumeric characters and the following special characters: ._-')


    def __call__(self, args):
        kwargs={}
        if args.unauthenticated_access and args.unauthenticated_access.lower() == 'true':
            kwargs['unauthenticated_access'] = True
        if args.unauthenticated_access and args.unauthenticated_access.lower() == 'false':
            kwargs['unauthenticated_access'] = False
        if args.description:
            kwargs['description'] = args.description
        if args.hypervisor:
            kwargs['hypervisor'] = args.hypervisor
        if args.new_name:
            kwargs['name'] = args.new_name
        if args.new_owner:
            kwargs['owner'] = args.new_owner
        if args.os_arch:
            kwargs['os_arch'] = args.os_arch
        if args.os_type:
            kwargs['os_type'] = args.os_type
        if args.os_variant:
            kwargs['os_variant'] = args.os_variant

        image_name = args.image
        if args.owner:
            image_name = "%s/%s" % (args.owner, args.image)

        try:
            self.get_repoman_client(args).modify_image(image_name, **kwargs)
            print "[OK]     Modifying image."
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not modify image '%s'" % (args.image), e)
