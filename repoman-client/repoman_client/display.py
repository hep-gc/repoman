from pprint import pprint
import copy
import datetime
import calendar
import time

# Single line listings of users/groups/images
def display_user(user, short_output=False, full_output=False, format_string=None):
    if short_output:
        print user['user_name']
    elif full_output:
        _pprint_dict(user)
    else:
        print format_string % (user['user_name'], user['full_name'], user['client_dn'])
        

def display_image(image, short_output=False, full_output=False, urls=False, format_string=None):
    # Convert times to local timezone first.
    # This is a bit of a hack because the server does not give us a tz independant
    # value and we must assume that the value given to us is a ctime in UTC and
    # then do some conversion.
    # This should be fixed by modifying the server to return timezone independant
    # values, such as epoch values, and then clean up the block of code below.
    image_copy = copy.deepcopy(image)
    if image_copy['modified'] != None:
        image_copy['modified'] = datetime.datetime.fromtimestamp(calendar.timegm(time.strptime(image['modified']))).ctime()
    if image_copy['uploaded'] != None:
        image_copy['uploaded'] = datetime.datetime.fromtimestamp(calendar.timegm(time.strptime(image['uploaded']))).ctime()
    if image_copy['expires'] != None:
        image_copy['expires'] = datetime.datetime.fromtimestamp(calendar.timegm(time.strptime(image['expires']))).ctime()

    if short_output:
        print "%s/%s" % (image_copy['owner'], image_copy['name'])
    elif full_output:
        _pprint_dict(image_copy)
    elif urls:
        print "%s/%s" % (image_copy['owner'].rsplit('/', 1)[-1], image_copy['name'])
        hypervisors = image_copy['hypervisor'].split(',')
        if image_copy['http_file_url'] != None:
            for hypervisor in hypervisors:
                print "  %s" % (image_copy['http_file_url'].replace('__hypervisor__', hypervisor))
        if image_copy['file_url'] != None:
            for hypervisor in hypervisors:
                print "  %s" % (image_copy['file_url'].replace('__hypervisor__', hypervisor))
        print ""
    else:
        print format_string % (image_copy['name'], image_copy['owner'], image_copy['hypervisor'], str(image_copy['size']), image_copy['modified'], image_copy['description'])

def display_group(group, short_output=False, full_output=False, format_string=None):
    if short_output:
        print group['name']
    elif full_output:
        _pprint_dict(group)
    else:
        print format_string % (group['name'], group['users'])

def display_user_list(users, short_output=False, full_output=False):
    format_string = None
    header = None
    if not short_output and not full_output:
        column_headers = ['Username', 'Full Name', 'Client DN']
        (format_string, header) = get_format_string(users, ['user_name', 'full_name', 'client_dn'], column_headers, ['l', 'l', 'l'])
        print header
    for user in sorted(users, key = lambda user : user['user_name'].lower()):
        display_user(user, short_output=short_output, full_output=full_output, format_string=format_string)

def display_image_list(images, short_output=False, full_output=False, urls=False):
    format_string = None
    header = None
    # Make a deep copy cause we are going to modify it if needed.
    images_copy = copy.deepcopy(images)

    # Shorten owner's names.
    for image in images_copy:
        image['owner'] = image['owner'].rsplit('/', 1)[-1]

    if not short_output and not full_output:
        column_headers = ['Image Name',
                          'Owner',
                          'Hypervisor', 
                          'Size',
                          'Last Modified',
                          'Description']
        (format_string, header) = get_format_string(images_copy, ['name', 'owner', 'hypervisor', 'size', 'modified', 'description'], column_headers, ['l', 'l', 'l', 'r', 'l', 'l'])
        print header
        
    # Let's print each image.
    for image in sorted(images_copy, key = lambda image : image['name'].lower()):
        display_image(image, short_output=short_output, full_output=full_output, urls=urls, format_string=format_string)


def display_group_list(groups, short_output=False, full_output=False):
    format_string = None
    header = None
    # Make a deep copy cause we are going to modify it if needed.
    groups_copy = copy.deepcopy(groups)

    if not short_output and not full_output:
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
        display_group(group, short_output=short_output, full_output=full_output, format_string=format_string)


# Print detailed descriptions of user/groups/images
def _pprint_dict(d):
    # find max key width
    max_key_width = 0
    for key in d.keys():
        if len(key) > max_key_width:
            max_key_width = len(key)
    format_string = '%%%ds : %%s' % (max_key_width)
    for key in sorted(d.keys()):
        if isinstance(d[key], list):
            print format_string % (key, ', '.join(d[key]))
        else:
            print format_string % (key, d[key])
    print ''

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


