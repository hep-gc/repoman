import os
import sys



class SubCommand(object):
    """A baseclass that all subcommands must be subclassed from in order for
    automagic subcommand import to work.

    required methods:
        get_parser(self)
            - The must return an argparse.ArgumentParser object prepopulated
              with the command options.

        __call__(self, args, extra_args=None)
            - This is the entry point that will be called to execute the
              subcommand.
            - args - contains the parsed commandline args
            - extra_args - contains unparsed commandline args the option is
                           specified for the class.
            What you do from this point on is up to you.

    """
    validate_config = True      # If False, config.validate() will not be called
                                # before the subcommand is run.
                                # If the subcommand depends on configuration values
                                # this should remain True.
    hidden = False              # if True, this command will not appear in the help
    command_group = None        # the name of a group the command will be added to
    command = None              # the command
    alias = None                # a short alias for the command
    parse_known_args = False    # determined if unknown commandline arguments
                                # will be allowed and passed to the __call__ method
    description = ""            # a description string that will show up in a
                                # list of subcommands

    def get_parser(self):
        # Raise an exception to make sure people override this in the subclass
        raise Exception("You need to override the 'get_parser' class method")

    def __call__(self, args, extra_args=None):
        # Raise an exception to make sure people override this in the subclass
        raise Exception("You need to override the '__call__' class method")



#def automagic_command_import(path):
#    _excludes = ['__init__.py']
#    subcommands = []

#    for f in os.listdir(path):
#        print f
#        if f.endswith('.py') and f not in _excludes:
#            toplevel = f.rsplit('.py')[0]
#            try:
#                module = __import__(path+'/'+toplevel, level=0) #filename imports not allowed
#            except Exception, e:
#                print e
#                continue

#            for c in dir(module):
#                print "\t%s%s" % (module, c)
#                try:
#                    cmd = getattr(module, c, None)
#                    if issubclass(cmd, SubCommand) and cmd is not SubCommand:
#                        subcommands.append(cmd)
#                except:
#                    pass
#    return subcommands

