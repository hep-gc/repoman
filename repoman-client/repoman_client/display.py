from pprint import pprint


# Single line listings of users/groups/images
def display_user(user, long_output=False):
    if not long_output:
        print user.rsplit('/', 1)[-1]
    else:
        print user

def display_image(image, long_output=False, urls=False, format_string=None):
    if long_output:
        # Image Name   Owner   Size    Last Modified          Description
        print format_string % (image['name'], image['owner'].rsplit('/', 1)[-1], str(image['size']), image['modified'], image['description'])
    elif urls:
        print "%s/%s" % (image['owner'].rsplit('/', 1)[-1], image['name'])
        if image['http_file_url'] != None:
            print "  %s" % (image['http_file_url'])
        if image['file_url'] != None:
            print "  %s" % (image['file_url'])
        print ""
    else:
        print "%s/%s" % (image['owner'].rsplit('/', 1)[-1], image['name'])

def display_group(group, long_output=False):
    if not long_output:
        print group.rsplit('/', 1)[-1]
    else:
        print group

def display_user_list(users, long_output=False):
    for user in sorted(users):
        display_user(user, long_output)

def display_image_list(images, long_output=False, urls=False):
    format_string = None
    if long_output:
        # Compute max field lengths
        max_feild_lengths = [0,0,0,0,0]
        for image in images:
            max_feild_lengths[0] = max(len(image['name']), max_feild_lengths[0])
            max_feild_lengths[1] = max(len(image['owner'].rsplit('/', 1)[-1]), max_feild_lengths[1])
            max_feild_lengths[2] = max(len(str(image['size'])), max_feild_lengths[2])
            max_feild_lengths[3] = max(len(image['modified']), max_feild_lengths[3])
            if image['description'] != None:
                max_feild_lengths[4] = max(len(image['description']), max_feild_lengths[4])

        # Create a format string used to format output lines.
        # Edit the 'format_string' variable below if you want to change
        # the output format (i.e., change field width, alignment, etc. )
        format_string = "%%-%ds %%-%ds %%%ds %%-%ds %%-%ds" % (max_feild_lengths[0], 
                                                              max_feild_lengths[1], 
                                                              max_feild_lengths[2], 
                                                              max_feild_lengths[3], 
                                                              max_feild_lengths[4])

        # Print a header with column names and horizontal line.
        print format_string % ("Image Name", "Owner", "Size", "Last Modified", "Description")
        print format_string % ('-' * max_feild_lengths[0], '-' * max_feild_lengths[1], '-' * max_feild_lengths[2], '-' * max_feild_lengths[3], '-' * max_feild_lengths[4])

    # Let's print each image.
    for image in sorted(images, key = lambda image : image['name'].lower()):
        display_image(image, long_output, urls, format_string)


def display_group_list(groups, long_output=False):
    for group in sorted(groups):
        display_group(group, long_output)


# detailed descriptions of user/groups/images
def describe_user(user, long_output=False):
    _pprint_dict(user)

def describe_group(group, long_output=False):
    _pprint_dict(group)

def describe_image(image, long_output=False):
    _pprint_dict(image)

def _pprint_dict(d):
    # find max key width
    max_key_width = 0
    for key in d.keys():
        if len(key) > max_key_width:
            max_key_width = len(key)
    format_string = '%%%ds : %%s' % (max_key_width)
    for key in sorted(d.keys()):
        print format_string % (key, d[key])


