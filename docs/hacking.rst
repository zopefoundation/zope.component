Hacking on :mod:`zope.component`
================================


Getting the Code
################

The main repository for :mod:`zope.component` is in the Zope Foundation
Github repository:

  https://github.com/zopefoundation/zope.component

You can get a read-only checkout from there:

.. code-block:: sh

   $ git clone https://github.com/zopefoundation/zope.component.git

or fork it and get a writeable checkout of your fork:

.. code-block:: sh

   $ git clone git@github.com/jrandom/zope.component.git

The project also mirrors the trunk from the Github repository as a
Bazaar branch on Launchpad:

https://code.launchpad.net/zope.component

You can branch the trunk from there using Bazaar:

.. code-block:: sh

   $ bzr branch lp:zope.component


Working in a ``virtualenv``
###########################

Installing
----------

If you use the ``virtualenv`` package to create lightweight Python
development environments, you can run the tests using nothing more
than the ``python`` binary in a virtualenv.  First, create a scratch
environment:

.. code-block:: sh

   $ /path/to/virtualenv --no-site-packages /tmp/hack-zope.component

Next, get this package registered as a "development egg" in the
environment:

.. code-block:: sh

   $ /tmp/hack-zope.component/bin/python setup.py develop

Running the tests
-----------------

Run the tests using the build-in ``setuptools`` testrunner:

.. code-block:: sh

   $ /tmp/hack-zope.component/bin/python setup.py test -q
   .........................................................................................................................................................................................................................................................
   ----------------------------------------------------------------------
   Ran 249 tests in 0.000s

   OK

If you have the :mod:`nose` package installed in the virtualenv, you can
use its testrunner too:

.. code-block:: sh

   $ /tmp/hack-zope.component/bin/nosetests
   .......................................................................................................................................................................................................................................................................
   ----------------------------------------------------------------------
   Ran 263 tests in 0.000s

   OK

If you have the :mod:`coverage` pacakge installed in the virtualenv,
you can see how well the tests cover the code:

.. code-block:: sh

   $ /tmp/hack-zope.component/bin/easy_install nose coverage
   ...
   $ /tmp/hack-zope.component/bin/nosetests --with coverage
   .......................................................................................................................................................................................................................................................................
   Name                                   Stmts   Miss  Cover   Missing
   --------------------------------------------------------------------
   zope/component.py                         42      0   100%
   zope/component/_api.py                   132      0   100%
   zope/component/_compat.py                  3      0   100%
   zope/component/_declaration.py            30      0   100%
   zope/component/event.py                   10      0   100%
   zope/component/eventtesting.py            11      0   100%
   zope/component/factory.py                 20      0   100%
   zope/component/globalregistry.py          38      0   100%
   zope/component/hookable.py                14      0   100%
   zope/component/hooks.py                   70      0   100%
   zope/component/interface.py               63      0   100%
   zope/component/interfaces.py              63      0   100%
   zope/component/persistentregistry.py      32      0   100%
   zope/component/registry.py                24      0   100%
   zope/component/security.py                65      0   100%
   zope/component/standalonetests.py          2      0   100%
   zope/component/zcml.py                   207      0   100%
   --------------------------------------------------------------------
   TOTAL                                    826      0   100%
   ----------------------------------------------------------------------
   Ran 263 tests in 0.000s

   OK


Building the documentation
--------------------------

:mod:`zope.component` uses the nifty :mod:`Sphinx` documentation system
for building its docs.  Using the same virtualenv you set up to run the
tests, you can build the docs:

.. code-block:: sh

   $ /tmp/hack-zope.component/bin/easy_install \
    Sphinx repoze.sphinx.autoitnerface zope.component
   ...
   $ cd docs
   $ PATH=/tmp/hack-zope.component/bin:$PATH make html
   sphinx-build -b html -d _build/doctrees   . _build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in _build/html.

You can also test the code snippets in the documentation:

.. code-block:: sh

   $ PATH=/tmp/hack-zope.component/bin:$PATH make doctest
   sphinx-build -b doctest -d _build/doctrees   . _build/doctest
   ...
   running tests...

   ...

   Doctest summary
   ===============
     964 tests
       0 failures in tests
       0 failures in setup code
       0 failures in cleanup code
   build succeeded.
   Testing of doctests in the sources finished, look at the  results in _build/doctest/output.txt.



Using :mod:`zc.buildout`
########################

Setting up the buildout
-----------------------

:mod:`zope.component` ships with its own :file:`buildout.cfg` file and
:file:`bootstrap.py` for setting up a development buildout:

.. code-block:: sh

   $ /path/to/python2.7 bootstrap.py
   ...
   Generated script '.../bin/buildout'
   $ bin/buildout
   Develop: '/home/jrandom/projects/Zope/zope.component/.'
   ...
   Got coverage 3.7.1

Running the tests
-----------------

You can now run the tests:

.. code-block:: sh

   $ bin/test --all
   Running zope.testing.testrunner.layer.UnitTests tests:
     Set up zope.testing.testrunner.layer.UnitTests in 0.000 seconds.
     Ran 249 tests with 0 failures and 0 errors in 0.000 seconds.
   Tearing down left over layers:
     Tear down zope.testing.testrunner.layer.UnitTests in 0.000 seconds.



Using :mod:`tox`
################

Running Tests on Multiple Python Versions
-----------------------------------------

`tox <http://tox.testrun.org/latest/>`_ is a Python-based test automation
tool designed to run tests against multiple Python versions.  It creates
a ``virtualenv`` for each configured version, installs the current package
and configured dependencies into each ``virtualenv``, and then runs the
configured commands.

:mod:`zope.component` configures the following :mod:`tox` environments via
its ``tox.ini`` file:

- The ``py26``, ``py27``, ``py33``, ``py34``, and ``pypy`` environments
  builds a ``virtualenv`` with the appropriate interpreter, installs
  :mod:`zope.component` and dependencies, and runs the tests
  via ``python setup.py test -q``.

- The ``coverage`` environment builds a ``virtualenv`` with ``python2.6``,
  installs :mod:`zope.component`, installs
  :mod:`nose` and :mod:`coverage`, and runs ``nosetests`` with statement
  coverage.

- The ``docs`` environment builds a virtualenv with ``python2.6``, installs
  :mod:`zope.component`, installs ``Sphinx`` and
  dependencies, and then builds the docs and exercises the doctest snippets.

This example requires that you have a working ``python2.6`` on your path,
as well as installing ``tox``:

.. code-block:: sh

   $ tox -e py26
   GLOB sdist-make: /home/tseaver/projects/Zope/Z3/zopetoolkit/src/zope.component/setup.py
   py26 inst-nodeps: /home/tseaver/projects/Zope/Z3/zopetoolkit/src/zope.component/.tox/dist/zope.component-4.2.2.dev0.zip
   py26 runtests: PYTHONHASHSEED='3711600167'
   py26 runtests: commands[0] | python setup.py test -q
   running test

   ...

   running build_ext
   .........................................................................................................................................................................................................................................................
   ----------------------------------------------------------------------
   Ran 249 tests 0.000s

   OK
   ___________________________________ summary ____________________________________
     py26: commands succeeded
     congratulations :)


Running ``tox`` with no arguments runs all the configured environments,
including building the docs and testing their snippets:

.. code-block:: sh

   $ tox
   GLOB sdist-make: .../zope.component/setup.py
   py26 sdist-reinst: .../zope.component/.tox/dist/zope.component-4.0.2dev.zip
   ...
   Doctest summary
   ===============
     964 tests
       0 failures in tests
       0 failures in setup code
       0 failures in cleanup code
   build succeeded.
   ___________________________________ summary ____________________________________
     py26: commands succeeded
     py26min: commands succeeded
     py27: commands succeeded
     pypy: commands succeeded
     py32: commands succeeded
     py33: commands succeeded
     py34: commands succeeded
     coverage: commands succeeded
     docs: commands succeeded
     congratulations :)


Contributing to :mod:`zope.component`
#####################################

Submitting a Bug Report
-----------------------

:mod:`zope.component` tracks its bugs on Github:

  https://github.com/zopefoundation/zope.component/issues

Please submit bug reports and feature requests there.


Sharing Your Changes
--------------------

.. note::

   Please ensure that all tests are passing before you submit your code.
   If possible, your submission should include new tests for new features
   or bug fixes, although it is possible that you may have tested your
   new code by updating existing tests.

If have made a change you would like to share, the best route is to fork
the Githb repository, check out your fork, make your changes on a branch
in your fork, and push it.  You can then submit a pull request from your
branch:

  https://github.com/zopefoundation/zope.component/pulls

If you branched the code from Launchpad using Bazaar, you have another
option:  you can "push" your branch to Launchpad:

.. code-block:: sh

   $ bzr push lp:~jrandom/zope.component/cool_feature

After pushing your branch, you can link it to a bug report on Github,
or request that the maintainers merge your branch using the Launchpad
"merge request" feature.
