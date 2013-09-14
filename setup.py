#!/usr/bin/env python

import sys

if sys.version_info < (2, 4) or sys.version_info >= (3,):
    sys.stderr.write('ERROR: requires Python versions >= 2.4 and < 3.0\n')
    sys.exit(1)

from distutils.core import setup


setup(
    # GENERAL INFO
    name = 'eveapi',
    version = '1.2.9',
    description = 'Python library for accessing the EVE Online API.',
    author = 'Jamie van den Berge',
    author_email = 'jamie@hlekkir.com',
    url = 'https://github.com/ntt/eveapi',
    keywords = ('eve-online', 'api'),
    platforms = 'any',
    classifiers = (
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment',
    ),
    # CONTENTS
    zip_safe = True,
    py_modules = ['eveapi',],
)
