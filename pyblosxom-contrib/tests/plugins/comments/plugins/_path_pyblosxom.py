"""This file adds to sys.path to allow importing test code and pyblosxom source.

Copy it into your test directory, using svn cp, and use it like so:

  import _path_pyblosxom
  from tests.plugins import test_base
  from Pyblosxom import pyblosxom, tools

Don't symlink to it. A copy needs to exist in your test's directory for the
__file__ magic to work right.

NOTE(ryanbarrett): this is similar to what we do with the tests in
pyblosxom/tests, but it's ugly in both places. If you have any better ideas,
let us know, or add them to http://pyblosxom.sf.net/wiki/index.php/Tests.
"""

__author__ = 'Ryan Barrett <pyblosxom@ryanb.org>'
__url__ = 'http://pyblosxom.sourceforge.net/wiki/index.php/Tests'

import os, sys

for dir in ('../../../../../pyblosxom/', '../../../../'):
  path = os.path.join(os.path.dirname(__file__), dir)
  if path not in sys.path:
    sys.path.insert(0, path)
