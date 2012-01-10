import os, sys
import subprocess

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



def check_proxy(proxy_cert):
    if not os.path.isfile(proxy_cert):
        print "The proxy certificate: '%s' does not exist.\nGenerate a new cert or manually specify with '--proxy'" % proxy_cert
        return

    # Test expiration
    cmd = "openssl x509 -in %s -noout -checkend 0" % proxy_cert
    retcode = subprocess.call(cmd, shell=True)
    if retcode:
        print "The proxy certificate: '%s' is expired" % proxy_cert

def get_userid():
    user_id = os.environ.get('SUDO_UID')
    if not user_id:
        user_id = os.getuid()
    return user_id
