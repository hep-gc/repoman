major = '0.2'
minor = '1'
tag = 'rc5'
revision = ''
version = major

if minor:
    version += '.' + minor
if tag:
    version += tag
if revision:
    version += '-r' + revision

