from pprint import pprint


# Single line listings of users/groups/images
def display_user(user, long=False):
    if not long:
        print user.rsplit('/', 1)[-1]
    else:
        print user

def display_image(image, long=False, preserve_user=True):
    if not long and not preserve_user:
        print image.rsplit('/', 1)[-1]
    elif not long and preserve_user:
        name = image.rsplit('/', 2)
        print name[-2] + '/' + name[-1]
    else:
        print image

def display_group(group, long=False):
    if not long:
        print group.rsplit('/', 1)[-1]
    else:
        print group

def display_user_list(users, long=False):
    for user in users:
        display_user(user, long)

def display_image_list(images, long=False):
    for image in images:
        display_image(image, long)

def display_group_list(groups, long=False):
    for group in groups:
        display_group(group, long)


# detailed descriptions of user/groups/images
def describe_user(user, long=False):
    pprint(user)

def describe_group(group, long=False):
    pprint(group)

def describe_image(image, long=False):
    pprint(image)

