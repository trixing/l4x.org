Pyblosxom plugin to render Bibtex files as entries

Here is a small module to render the contents of Bibtex (.bib) files as
Pyblosxom_ entries. The plugin is called `bib.py`_ and has no
configuration. Just put it in your plugins folder, activate it in the
``config.py`` file and drop a bibtex file in your entries folder. It will
create an unordered list, sorted by last name of the first author and year by
default, which can be customized either directly in the
source or via a CSS file. The plugin requires the Python ``bibtex``
module, available either from your nearest Debian_ mirror or the
Pybliographer_ distribution.

The title of the entry will either be derived from the filename or
from a special Bibtex ``@title`` entry:

::

  @TITLE{KeyDoesNotMatter,
          title={Blog entry title}
  }

See the result `of my RF MEMS specific bibliography </personal/rfmemsde.html>`_ 
and `my personal bibliography </personal/jdide.html>`_.

.. _bib.py: ./bib.py
.. _Pyblosxom: http://pyblosxom.sf.net
.. _Pybliographer: http://pybliographer.org
.. _Debian: http://packages.debian.org/python-bibtex
