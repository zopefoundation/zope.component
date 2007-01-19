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
"""Setup for zope.i18nmessageid package

$Id$
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.component',
      version='3.4-dev',
      url='http://svn.zope.org/zope.component',
      license='ZPL 2.1',
      description='Core of the Zope Component Architecture',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="This package, together with `zope.interface`,"
                       "provides facilities for defining, registering"
                       "and looking up components.  There are two basic"
                       "kinds of components: adapters and utilities.",
      
      packages=['zope',
                'zope.component',
                'zope.component.bbb',
                'zope.component.testfiles',
               ],
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['zope.deprecation',
                        'zope.exceptions',
                        'zope.interface',
                        'zope.deferredimport',
                        'zope.hookable',
                        'zope.event',
                        'zope.configuration',
                        'zope.security',
                        'zope.proxy',
                        'zope.i18nmessageid',
                        'zope.testing',
                       ],
      include_package_data = True,

      zip_safe = False,
      )
