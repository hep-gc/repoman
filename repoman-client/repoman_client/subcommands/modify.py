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
    command_group = "advanced"
    command = "modify-image"
    alias = 'mi'
    description = 'Modify an existing image with the given information'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "modify-image image [-h] [--name] [--description] [--os_variant] [--os_arch] [--os_type] [--hypervisor] [--read_only] [--expires] [--unauthenticated_access]"
        p.add_argument('image', help='The existing image you want to modify')
        p.add_argument('--name', help='image name unique to the users namespace')
        p.add_argument('--description', help='description of the image modification')
        p.add_argument('--os_variant', help='redhat, centos, ubuntu, etc')
        p.add_argument('--os_arch', help='x86, x86_64')
        p.add_argument('--os_type', help='linux, unix, windows, etc')
        p.add_argument('--hypervisor', help='kvm, xen')
        p.add_argument('--read_only', default=False, help='should the image be read only?')
        p.add_argument('--expires', help='when should the image expire?')
        p.add_argument('--unauthenticated_access', default=True, help='should the image access be unauthenticated?')
        return p

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('ModifyImage')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
    
        repo = RepomanClient(config.host, config.port, config.proxy)
  
        kwargs={}
        extra_args=['name',args.name,'description',args.description,'os_variant',args.os_variant,'os_arch',args.os_arch,'os_type',args.os_type,
                   'hypervisor',args.hypervisor,'read_only',args.read_only,'expires',args.expires,'unauthenticated_access',args.unauthenticated_access]
        for arg,value in arg_value_pairs(extra_args):
            if value:
                if value in ['true', 'True', 'TRUE']:
                    value = True
                elif value in ['false', 'False', 'FALSE']:
                    value = False
                kwargs.update({arg:value})
        del extra_args    
        log.debug("kwargs: '%s'" % kwargs)

        try:
            repo.modify_image(args.image, **kwargs)
            print "[OK]     Modifying image."
        except RepomanError, e:
            print "[FAILED] Modifying image.\n\t-%s" % e
            sys.exit(1)



class Rename(SubCommand):
    command = 'rename'
    alias = 'rn'
    description = "Rename an existing image from 'old' to 'new'"

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('old', help='name of exiting image')
        p.add_argument('new', help='new name that existing image will get')
        return p

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('Rename')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
        
        repo = RepomanClient(config.host, config.port, config.proxy)

        kwargs = {'name':args.new}
        log.debug("kwargs: '%s'" % kwargs)
        try:
            repo.modify_image(args.old, **kwargs)
            print "[OK]     Renaming image."
        except RepomanError, e:
            print "[FAILED] Renaming image.\n\t-%s" % e
            sys.exit(1)

