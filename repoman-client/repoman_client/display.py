from pprint import pprint
import copy

# Single line listings of users/groups/images
def display_user(user, long_output=False, format_string=None):
    if not long_output:
        print user['user_name']
    else:
        print format_string % (user['user_name'], user['full_name'], user['client_dn'])

def display_image(image, long_output=False, urls=False, format_string=None):
    if long_output:
        print format_string % (image['name'], image['owner'], str(image['size']), image['modified'], image['description'])
    elif urls:
        print "%s/%s" % (image['owner'].rsplit('/', 1)[-1], image['name'])
        if image['http_file_url'] != None:
            print "  %s" % (image['http_file_url'])
        if image['file_url'] != None:
            print "  %s" % (image['file_url'])
        print ""
    else:
        print "%s/%s" % (image['owner'], image['name'])

def display_group(group, long_output=False, format_string=None):
    if not long_output:
        print group['name']
    else:
        print format_string % (group['name'], group['users'])

def display_user_list(users, long_output=False):
    format_string = None
    header = None
    if long_output:
        column_headers = ['Username', 'Full Name', 'Client DN']
        (format_string, header) = get_format_string(users, ['user_name', 'full_name', 'client_dn'], column_headers, ['l', 'l', 'l'])
        print header
    for user in sorted(users, key = lambda user : user['user_name'].lower()):
        display_user(user, long_output, format_string)

def display_image_list(images, long_output=False, urls=False):
    format_string = None
    header = None
    # Make a deep copy cause we are going to modify it if needed.
    images_copy = copy.deepcopy(images)

    # Shorten owner's names.
    for image in images_copy:
        image['owner'] = image['owner'].rsplit('/', 1)[-1]

    if long_output:
        column_headers = ['Image Name',
                          'Owner',
                          'Size',
                          'Last Modified',
                          'Description']
        (format_string, header) = get_format_string(images_copy, ['name', 'owner', 'size', 'modified', 'description'], column_headers, ['l', 'l', 'r', 'l', 'l'])
        print header
        
    # Let's print each image.
    for image in sorted(images_copy, key = lambda image : image['name'].lower()):
        display_image(image, long_output, urls, format_string)


def display_group_list(groups, long_output=False):
    format_string = None
    header = None
    # Make a deep copy cause we are going to modify it if needed.
    groups_copy = copy.deepcopy(groups)

    if long_output:
        # Shorten the users list (user URL -> username)
        for group in groups_copy:
            users = []
            for user in group['users']:
                users.append(user.rsplit('/', 1)[-1])
            group['users'] = ','.join(sorted(users))

        column_headers = ['Group Name', 'Members']
        (format_string, header) = get_format_string(groups_copy, ['name', 'users'], column_headers, ['l', 'l'])
        print header
    for group in sorted(groups_copy, key = lambda group : group['name'].lower()):
        display_group(group, long_output, format_string)


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



# Use this method to get a format string that will nicely align
# the columns in a multi-column output of a list of items.
# TODO: Document this...
def get_format_string(items, keys, column_headers, justification = None):
    # Compute max field lengths
    max_feild_lengths = []
    
    # First, lets set intial values to length of headers.
    for header in column_headers:
        max_feild_lengths.append(len(header))
    for item in items:
        i = 0
        for key in keys:
            if item[key] != None:
                max_feild_lengths[i] = max(len(str(item[key])), max_feild_lengths[i])
            i += 1

    # Create a format string used to format output lines.
    format_strings = []
    i = 0
    for fl in max_feild_lengths:
        format_string = '%'
        if justification != None and justification[i] == 'l':
            format_string += '-'
        format_string += '%ds' % (fl)
        format_strings.append(format_string)
        i += 1

    format_string = ' '.join(format_strings)

    # Create header and underline
    header = format_string % tuple(column_headers)
    underlines = []
    for fl in max_feild_lengths:
        underlines.append('-' * fl)
    header += '\n' + format_string % tuple(underlines)

    return (format_string, header)


