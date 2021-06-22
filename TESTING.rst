Running the tests with Tox
==========================

We assume you have ``tox`` installed globally.
If not, create a virtualenv somewhere and do ``pip install tox``.
Then run the tests for all Plone versions like this::

    bin/tox -pauto

This will create a ``.tox`` directory with sub directories for each specified Plone version.
You can go to such a sub directory and run bin/test from there too.

See ``tox.ini`` for the versions, mostly the environments in ``[tox] envlist``.

To run only the test for one environment, say Plone 4.3::

    bin/tox -e 4.3-py27


Running a Plone instance
========================

The buildout configs contain two parts: test and instance.
Tox explicitly only installs test.
If you want a Plone instance:

- Either edit ``tox.ini`` to install both test and instance.  This gives you a Plone instance in all relevant versions. But any time you run tox, you may lose your data.
- Or create a virtualenv in the current directory, ``bin/pip install zc.buildout``, and call ``bin/buildout -c test-5.2.cfg`` or whatever config you want.
