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

setup(name='repoman-client',
    version=version,
    description='Client to connect to Repoman image repository.',
    author='Kyle Fransham, Drew Harris, Matthew Vliet',
    author_email='fransham@uvic.ca, dbharris@uvic.ca, mvliet@uvic.ca',
    url='http://github.com/hep-gc/repoman',
    install_requires=["simplejson","argparse"],
    packages=['repoman_client'],
    scripts=['scripts/repoman'],
    include_package_data=True,
    zip_safe=False,
)

