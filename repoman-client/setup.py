#!/usr/bin/env python
from repoman_client.__version__ import version
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
from distutils.dir_util import mkpath
import os.path
import subprocess
import shutil

setup(name='repoman-client',
    version=version,
    description='Client to connect to Repoman image repository.',
    author='Kyle Fransham, Drew Harris, Matthew Vliet',
    author_email='fransham@uvic.ca, dbharris@uvic.ca, mvliet@uvic.ca',
    url='http://github.com/hep-gc/repoman',
    install_requires=["simplejson","argparse"],
    packages=['repoman_client'],
    scripts=['repoman'],
    include_package_data=True,
    zip_safe=False,
)

# Attempt to install manpage if running as root.
try:
    if os.getuid() == 0:
        print 'Installing repoman man pages...'
        p = subprocess.Popen(['manpath'], stdout=subprocess.PIPE)
        output = p.communicate()[0]
        if len(output) > 0:
            manpath = output.split(':')[-1].strip()
            manpath = os.path.join(manpath, 'man1')
            if not os.path.exists(manpath):
                os.makedirs(manpath)
            shutil.copy2('doc/man/repoman.1', manpath)
            print 'Updating man database...'
            r = subprocess.call(["mandb"])
            if r != 0:
                print 'Error updating man database.'
except Exception, e:
    print 'Error installing repoman man pages.\n%s' % (e)
