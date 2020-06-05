======
Entomb
======

    Keep your important files safe.

    Make them unable to be modified or deleted by **any** user, even root.


Installation
------------

::

    $ pip install entomb


How it works
------------

Entomb recursively sets/unsets the immutable attribute on all files on a path
using the `chattr <https://en.wikipedia.org/wiki/Chattr>`_  command.

Files in ``.git`` directories are ignored by default, but can be included.

The immutable attribute is never set on directories, because this would stop
files being created in those directories. Entomb works on files only.

At the moment Entomb only works on Linux.

Entomb has no dependencies.


Examples
--------

::

    # Make all files in ~/photos immutable.
    entomb.py ~/photos

    # List all files in ~/photos which are not immutable.
    entomb.py --list-mutable ~/photos

    # Report on how many files in ~/photos are and aren't immutable.
    entomb.py --report ~/photos

    # Do a dry run on ~/photos, including any git files/directories.
    entomb.py -d -g ~/photos

    # Make all files in ~/photos mutable (i.e. unset the immutable attribute).
    entomb.py -u ~/photos


Usage
-----

::

    $ ./entomb.py --help
    usage: entomb.py [options] path

    Manage file immutability.

    positional arguments:
      path               the path to operate on

    optional arguments:
      -h, --help         show this help message and exit
      -d, --dry-run      make no changes
      -g, --include-git  include .git directories (excluded by default)
      --list-immutable   list all immutable files
      --list-mutable     list all mutable files
      -r, --report       display a status report
      -u, --unset        unset immutability


Development
-----------

Get set up, preferably in a virtualenv::

    $ make init
    $ make install

Lint the code::

    $ make lint

Run the tests::

    $ make test

Check the test coverage::

    $ make coverage


Releasing
---------

#. Check out the ``master`` branch.

#. Ensure ``CHANGELOG.rst`` includes everything to go in the release and is
   committed.

#. Ensure everything to go in the release is committed.

#. Increment the version in ``__init__.py``.

#. Shift everything in the **Unreleased** section of ``CHANGELOG.rst`` to a new
   section named with the new version number and the current date.

#. Ensure CI runs without warnings or errors::

    $ make ci

#. Make and tag the release commit::

    $ make release

#. Build the package::

    $ make package

#. Publish the package to PyPI::

    $ make publish

#. Push to the repo and clean up packaging artifacts::

    $ make push
    $ make clean

#. Create a GitHub release.


Code style
----------

#. Only modules are imported. Classes, functions and variables are not imported
   directly.

#. A module's functions are ordered alphabetically.

#. A module's private functions are placed alphabetically at the bottom of the
   module.

#. Docstrings follow the `NumPy docstring guide
   <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

#. Strings are enclosed with double quotes.

#. The last item of a multi-line dictionary or list has a trailing comma.


Changes
-------

For what has changed in each version, see ``CHANGELOG.rst``.
