from repoman_client.config import config
from repoman_client.__version__ import version
import argparse
import sys

__all__ = ['RepomanCLI']


class RepomanCLI(object):
    def __init__(self):
        self.version = version
        self.parser = None
        self.subparser = None
        self.subcommands = {}
        self._init_parser()

    def _init_parser(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument('-h', '--host')
        self.parser.add_argument('-p', '--port')
        self.parser.add_argument('-P', '--proxy')
        self.subparser = self.parser.add_subparsers(dest='subcommand')
        
    def get_parser(self):
        return self.parser

    def get_subparser(self):
        return self.subparser

    def print_help(self, subcommand):
        if subcommand == None:
            self.parser.print_help()
        elif subcommand in self.subcommands:
            self.subcommands[subcommand].print_help()

    def add_subcommand(self, subcommand):
        self.subcommands[subcommand.command] = subcommand

# Singleton instance of RepomanCLI:
repoman_cli = RepomanCLI()

