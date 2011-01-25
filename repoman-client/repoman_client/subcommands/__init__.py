

import os
import sys
from repoman_client.subcommand import SubCommand

_excludes = ['__init__.py']
subcommands = []


# Search subcommands folder for any subclass of SubCommand
# Steps:
#   1. try to import each file in the subcommands directory
#   2. search each imported file for subclasses of SubCommand
#       - if a subclass is found, it is added to the subcommands list
for f in os.listdir(__path__[0]):
    if f.endswith('.py') and f not in _excludes:
        toplevel = f.rsplit('.py')[0]
        try:
            module = __import__(toplevel, globals=globals())
        except:
            continue

        for c in dir(module):
            try:
                cmd = getattr(module, c, None)
                if issubclass(cmd, SubCommand) and cmd is not SubCommand:
                    subcommands.append(cmd)
            except:
                pass

