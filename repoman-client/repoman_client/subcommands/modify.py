from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from argparse import ArgumentParser
import sys
import logging

class ModifyUser(SubCommand):
    command = "modify-user"
    alias = 'mu'
    description = 'Modify a repoman user with the given metadata information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('user', help = 'The name of the user to be modified.  See "repoman list-users" to see possible values.')
        self.get_arg_parser().add_argument('-c', '--client_dn', metavar = 'dn', help = 'The Distinguised Name (DN) of the certificate which is owned by the user.')
        self.get_arg_parser().add_argument('-f', '--full_name', metavar = 'name', help = 'The full name of the user.')
        self.get_arg_parser().add_argument('-e', '--email', metavar = 'address', help = 'The email address of the user.')
        self.get_arg_parser().add_argument('-n', '--new_name', metavar = 'user', help = 'The new unique username for the user.')
        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)

        kwargs = {}
        if args.full_name:
            kwargs['full_name'] = args.full_name
        if args.email:
            kwargs['email'] = args.email
        if args.new_name:
            kwargs['user_name'] = args.new_name
        if args.client_dn:
            kwargs['client_dn'] = args.client_dn

        try:
            repo.modify_user(args.user, **kwargs)
            print "[OK]     Modifying user."
        except RepomanError, e:
            print "[FAILED] Modifying user.\n\t-%s" % e
            sys.exit(1)



class ModifyGroup(SubCommand):
    command = "modify-group"
    alias = 'mg'
    description = 'Modify a group with the given information.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        # Subcommand: modify-group
        self.get_arg_parser().add_argument('group', help = 'The group you want to modify. Use "repoman list-groups" to see possible values.')
        self.get_arg_parser().add_argument('-n', '--new_name', metavar = 'value', help = 'The name of the group. It must be  unique and can only contain ([a-Z][0-9][_][-]) characters.')
        self.get_arg_parser().add_argument('-p', '--permissions', metavar = 'permission', nargs = '+', help = 'The permissions that the members of the group have (Blank separated  list  Ex:  ´user_delete  image_modify´).   Possible   values   are:   group_create,  group_delete, group_modify, group_modify_membership, group_modify_permissions, image_create,  image_delete,  image_delete_group,  image_modify, image_modify_group,   user_create,   user_delete,   user_modify, user_modify_self.  See repoman manpage description of each permission.')
        self.get_arg_parser().add_argument('-u', '--users', metavar = 'user', nargs='+', help = 'The users that  are  members  of  the  group.  (Blank separated list) Ex: ´msmith sjobs´')
        self.get_arg_parser().set_defaults(func=self)

        

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        kwargs={}
        if args.new_name:
            kwargs['name'] = args.new_name
        if args.permissions:
            kwargs['permissions'] = args.permissions
        if args.users:
            kwargs['users'] = args.users

        try:
            repo.modify_group(args.group, **kwargs)
            print "[OK]     Modifying group."
        except RepomanError, e:
            print "[FAILED] Modifying group.\n\t-%s" % e
            sys.exit(1)



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
        self.get_arg_parser().add_argument('-n', '--new_name', metavar = 'value', help = 'The new name of the image-slot on the repository.  This  will be used to reference the image when running other repoman commands. It must be unique  to  the  owner\'s domain and can only contain ([a-Z][0-9][_][-]) characters.') 
        self.get_arg_parser().add_argument('-o', '--new_owner', metavar = 'user', help = 'The new owner of the named image. Use "repoman list-users" to see possible values.')
        self.get_arg_parser().add_argument('--os_arch', choices = ['x86', 'x86_64'], help = 'The  operating  system  architecture.')
        self.get_arg_parser().add_argument('--os_type', metavar = 'value', help = 'The operating system type.  Ex:  linux,  unix, windows, etc.')
        self.get_arg_parser().add_argument('--os_variant', metavar = 'value', help = 'The operating system variant. Ex: redhat, centos, ubuntu, etc.')
        self.get_arg_parser().set_defaults(func=self)


    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
  
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
            print 'Changing the owner of an image has not been implemented yet.'
            sys.exit(1)
            #kwargs['owner'] = args.owner
        if args.os_arch:
            kwargs['os_arch'] = args.os_arch
        if args.os_type:
            kwargs['os_type'] = args.os_type
        if args.os_variant:
            kwargs['os_variant'] = args.os_variant

        try:
            repo.modify_image(args.image, **kwargs)
            print "[OK]     Modifying image."
        except RepomanError, e:
            print "[FAILED] Modifying image.\n\t-%s" % e
            sys.exit(1)

