from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError, arg_value_pairs
from argparse import ArgumentParser
import sys
import logging

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
        log = logging.getLogger('ModifyUser')
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
        log = logging.getLogger('ModifyGroup')
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

