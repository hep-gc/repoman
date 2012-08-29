major = '0.2'
minor = '5'
tag = None
revision = ''
version = major

if minor:
    version += '.' + minor
if tag:
    version += tag
if revision:
    version += '-r' + revision

