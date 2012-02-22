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


def get_userid():
    user_id = os.environ.get('SUDO_UID')
    if not user_id:
        user_id = os.getuid()
    return user_id
