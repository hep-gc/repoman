major = '0.2'
minor = ''
tag = ''
revision = ''
version = major

if minor:
    version += '.' + minor
if tag:
    version += tag
if revision:
    version += '-r' + revision

