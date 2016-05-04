#!/usr/bin/env python

import io
import re
import sys

if sys.version_info < (2, 6):
    sys.stderr.write('ERROR: requires Python versions >= 2.6 or 3.3+\n')
    sys.exit(1)

from setuptools import setup


def find_version(filename):
    """Uses re to pull out the assigned value to __version__ in filename."""

    with io.open(filename, "r", encoding="utf-8") as version_file:
        version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                                  version_file.read(), re.M)
    if version_match:
        return version_match.group(1)
    return "0.0.0"


setup(
    # GENERAL INFO
    name='eveapi',
    version=find_version("eveapi.py"),
    description='Python library for accessing the EVE Online API.',
    author='Jamie van den Berge',
    author_email='jamie@hlekkir.com',
    url='https://github.com/ntt/eveapi',
    keywords=('eve-online', 'api'),
    platforms='any',
    install_requires=[
        'future>=0.15',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Games/Entertainment',
    ],
    # CONTENTS
    zip_safe=True,
    py_modules=['eveapi'],
)
