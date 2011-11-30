import os, sys

def yes_or_no(message="Confirm deletion [yes]/[n]o: "):
    answer = raw_input(message)
    attempts = 1
    while answer in ['y', 'ye']:
        if attempts >= 3:
            break
        answer = raw_input("Type the full word 'yes' to confirm: ")
        attempts = attempts + 1

    if answer.lower() in ['yes']:
        return True
    else:
        return False



def check_sudo(exit=False):
    # if uid = 0, return true
    if os.getuid() == 0:
        return True
    if exit:
        print "Error.  This command requires root privlidges, try again with sudo."
        sys.exit(1)
    return False
