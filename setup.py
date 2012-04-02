##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.component package
"""

import os
from setuptools import setup, find_packages


tests_require = [
    'ZODB3',
    'zope.hookable',
    'zope.testing',
    'zope.testrunner',
    ]


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.component',
    version='3.12.2.dev0',
    url='http://pypi.python.org/pypi/zope.component',
    license='ZPL 2.1',
    description='Zope Component Architecture',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zope', 'component', 'README.txt')
        + '\n' +
        read('src', 'zope', 'component', 'event.txt')
        + '\n' +
        read('src', 'zope', 'component', 'factory.txt')
        + '\n' +
        read('src', 'zope', 'component', 'registry.txt')
        + '\n' +
        read('src', 'zope', 'component', 'persistentregistry.txt')
        + '\n' +
        read('src', 'zope', 'component', 'socketexample.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '********\n'
        ),
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    namespace_packages=['zope',],
    tests_require = tests_require,
    install_requires=['setuptools',
                      'zope.interface>=3.8.0',
                      'zope.event',
                      ],
    include_package_data = True,
    zip_safe = False,
    extras_require = dict(
        hook = ['zope.hookable'],
        persistentregistry = ['ZODB3'],
        security = ['zope.location',
                    'zope.proxy',
                    'zope.security',
                    ],
        zcml = ['zope.configuration',
                'zope.i18nmessageid',
                ],
        test = tests_require,
        ),
    )
