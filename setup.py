##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Setup for zope.component package

$Id$
"""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.component',
    version = '3.6.0dev',
    url='http://pypi.python.org/pypi/zope.component',
    license='ZPL 2.1',
    description='Zope Component Architecture',
    author='Zope Corporation and Contributors',
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
        read('src', 'zope', 'component', 'registry.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    packages = find_packages('src'),
    package_dir = {'': 'src'},

    namespace_packages=['zope',],
    tests_require = ['zope.testing'],
    install_requires=['zope.deprecation',
                      'zope.interface',
                      'zope.deferredimport',
                      'zope.event',
                      'setuptools',
                      ],
    include_package_data = True,
    zip_safe = False,
    extras_require = dict(
        service = ['zope.exceptions'],
        zcml = ['zope.configuration',
                'zope.security',
                'zope.proxy',
                'zope.i18nmessageid',
                ],
        test = ['zope.testing',
                'ZODB3',
                'zope.hookable',
                'zope.location',
                ],
        hook = ['zope.hookable'],
        persistentregistry = ['ZODB3'],
        ),
    )
