import ConfigParser
from repoman_client.subcommand import SubCommand
from repoman_client.config import config
from argparse import ArgumentParser

class MakeConfig(SubCommand):
    validate_config = False
    command = 'make-config'
    description = 'Create a repoman client configuration file under your home directory.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('-E', '--system_excludes', metavar='system_paths',
                                   help = 'Blank separated list of paths to be excluded from a snapshot of the operating system during a "repoman save-image".  A directory path specification ending in "/*" will cause the directory to be created in the saved image, but none of it\'s contents to be copied to the saved image.  Defaults to "/cvmfs/* /dev/* /mnt/* /proc/* /root/.ssh /sys/* /tmp/*".')
        self.get_arg_parser().add_argument('-e', '--user-excludes', metavar='user_paths',
                                   help = 'Blank separated list of paths to be excluded from a snapshot of the operating system during a "repoman save-image".  A directory path specification ending in "/*" will cause the directory to be created in the saved image, but none of it\'s contents to be copied to the saved image.  Defaults to an empty list.')
        self.get_arg_parser().set_defaults(func=self)



    def __call__(self, args):
        print "Generating new default configuration file"
        # do nothing for now as we debug this new system...
        #config.generate_config()
        #print "Customization can be done by editing '%s'" % config.config_file


