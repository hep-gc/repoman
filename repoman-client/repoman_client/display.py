from pprint import pprint


# Single line listings of users/groups/images
def display_user(user, long=False):
    pprint(user)

def display_image(image, long=False):
    pprint(image)

def display_group(group, long=False):
    pprint(group)

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

