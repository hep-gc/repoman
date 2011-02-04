from repoman_client.config import config
import argparse
import sys
from pprint import pprint

__all__ = ['RepomanCLI']

def generate_help(title, commands):
    # Get the length of the longest command for formatting
    max_len = max([len(c.command) for c in commands])
    help_lines = ["%s:\n"%title.upper()]
    for c in commands:
        if not c.hidden:
            #left justify each command and print
            help_lines.append("    %s%s\n" % (c.command.ljust(max_len+4), c.description))
    return "".join(help_lines)


def arg_value_pairs(args):
    if len(args) % 2:
        raise ArgumentFormatError('Unable to parse argument/value pairs due to uneven number of values.')
    for x in range(0, len(args), 2):
        yield args[x], args[x+1]


def parse_unknown_args(args):
    """
    expect args to be a list in the form of:
        ['--arg1', 'value1', '--arg2', 'value', ...]
    therfor args must contain an even number of items.
    """
    arg_pairs = {}
    for arg, value in arg_value_pairs(args):
        if not arg.startswith('--'):
            raise ArgumentFormatError("Found a value first, check arg/value order.")
        else:
            if value in ['true', 'True', 'TRUE']:
                value = True
            elif value in ['false', 'False', 'FALSE']:
                value = False
            arg_pairs.update({arg.lstrip('--'):value})
    return arg_pairs


class ArgumentFormatError(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.__repr__



class CommandGroup(object):
    def __init__(self, title):
        self.title = title
        self.commands = []           # An ordered list used to generate help
        self.command_lookup = {}     # A dictionart to do command-->function lookups

    def format_help(self):
        return generate_help(self.title, self.commands)

    def add_command(self, command):
        if command not in self.commands:
            self.commands.append(command)
            self.command_lookup.update({command.command:command})
            if command.alias:
            	self.command_lookup.update({command.alias:command})

    def get_command(self, command):
        return self.command_lookup.get(command)



class RepomanCLI(object):
    def __init__(self, version):
        self.version = version
        self.parser = self.get_parser()
        self.commands = []              # list of commands with no group specified
        self.command_lookup = {}        # command string --> class lookup
        self.groups = []                # list of groups in order of appearence
        self.group_lookup = {}          # group_name --> class lookup

    def __call__(self):
        (args, extra) = self.parse_known_args()
        if args.help_all:
            self.print_help(long=True)
        elif args.help:
            self.print_help(long=False)

        if not args.subcommand:
            self.parser.error('Specify a subcommand to run, or run --help')

        # Overwrite config values with command line options if available
        if args.proxy:
            config.user_proxy_cert = args.proxy
        if args.host:
            config.repository_host = args.host
        if args.port:
            config.repository_port = args.port

        self.dispatch(args.subcommand, extra)

    def get_parser(self):
        p = argparse.ArgumentParser(add_help=False)
        p.add_argument('subcommand', metavar='SUBCOMMAND', nargs='?')
        p.add_argument('-h', '--help', action='store_true', default=False)
        p.add_argument('--help-all', action='store_true', default=False)
        p.add_argument('--version', action='version', version='%s' % self.version)
        p.add_argument('-H', '--host', help='Override host setting')
        p.add_argument('-P', '--port', type=int, help='Override port setting for host')
        p.add_argument('--proxy', help='Override default proxy certificate')
        return p

    def parse_known_args(self, args=None):
        if args is None:
            args = sys.argv[1:]

        # Bit of a hack to get the help for subcommands
        #   if '-h' or '--help' occur in the args in anyplace other args[0],
        #   it will be removed temporarily.  The main parser will be called,
        #   then the help switch will be re-inserted into the args and passed to
        #   the subcommand parser.
        if '-h' or '--help' in args:
            help_index = None
            try:
                help_index = args.index('-h')
            except ValueError:
                pass
            try:
                new_index = args.index('--help')
                if not help_index:
                    help_index = new_index
                elif help_index and new_index < help_index:
                    help_index = new_index
            except ValueError:
                pass

        help_extracted = False
        if help_index and help_index != 0:
            help_extracted = True
            [args.remove('--help') for i in range(args.count('--help'))]
            [args.remove('-h') for i in range(args.count('-h'))]

        (main_args, sub_args) = self.parser.parse_known_args(args)
        if help_extracted:
            sub_args.append('--help')

        return main_args, sub_args

    def print_help(self, long=False, exit=0):
        print self.parser.format_help()
        print generate_help('subcommands', self.commands)
        if long:
            for g in self.groups:
                print self.group_lookup[g].format_help()
        sys.exit(exit)

    def _add_command_group(self, group_name):
        if group_name not in self.groups:
            self.groups.append(group_name)
            group = CommandGroup(group_name)
            self.group_lookup.update({group_name:group})
            return group
        else:
            return self.group_lookup.get(group_name)

    def add_command(self, command_class):
        group = command_class.command_group or None
        if not group and command_class not in self.commands:
            self.commands.append(command_class)
            self.command_lookup.update({command_class.command:command_class})
            if command_class.alias:
            	self.command_lookup.update({command_class.alias:command_class})
        elif group:
            group = self._add_command_group(group)
            group.add_command(command_class)

    def lookup_command(self, command):
        cmd = self.command_lookup.get(command)
        if not cmd:
            for name, group in self.group_lookup.iteritems():
                cmd = group.get_command(command)
                if cmd:
                    break
        return cmd

    def dispatch(self, command, args):
        cmd = self.lookup_command(command)
        if cmd:
            cmd = cmd()
            cmd_parser = cmd.get_parser()
            cmd_parser.prog = command
            if cmd.parse_known_args:
                (args, extra) = cmd_parser.parse_known_args(args)
            else:
                args = cmd_parser.parse_args(args)
                extra = None
            if cmd.validate_config:
                config.validate()
            cmd(args, extra)
            sys.exit(0)
        else:
            print ("Invalid SubCommand.  Please run program with the '--help' "
                    "flag for available subcommands")
            sys.exit(1)

