
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

