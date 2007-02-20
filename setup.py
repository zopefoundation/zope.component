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
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


name = 'zope.component'
setup(name=name,
      version='3.4dev',
      url='http://www.python.org/pypi/'+name,
      license='ZPL 2.1',
      description='Core of the Zope Component Architecture',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="This package, together with `zope.interface`,"
                       "provides facilities for defining, registering"
                       "and looking up components.  There are two basic"
                       "kinds of components: adapters and utilities.",
      
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
          zcml = ['zope.configuration', 'zope.security', 'zope.proxy',
                  'zope.i18nmessageid',
                  #'zope.location', # should be depenency of zope.security
                  ],
          test = ['zope.testing',
                  'ZODB3',
                  #'zope.configuration', 'zope.security', 'zope.proxy',
                  #'zope.i18nmessageid',
                  #'zope.location', # should be depenency of zope.security
                  ],
          hook = ['zope.hookable'],
          persistentregistry = ['ZODB3'],
          ),
      )
