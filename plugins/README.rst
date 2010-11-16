Portico readme

===========================================================
Portico, a Pyblosxom plugin for entry based photo galleries
===========================================================

Portico_ is a Pyblosxom_ entry parser plugin for displaying small to medium
size photo galleries as a single blog entry. Portico blog entries are
displayed in three different ways, depending on the context:

.. _Portico: http://jw.n--tree.net/portico/
.. _Pyblosxom: http://pyblosxom.sourceforge.net/

  1) Displaying short series of thumbnails, whenever the entry is not
     individually rendered at its permanent URL (e.g. on the front page of
     your blog, amongst other entries).

  2) Displaying all the thumbnails for the collection, whenever the entry is
     rendered at its permanent URL.

  3) Slideshow-like, displaying a larger version of the photo, possibly
     including 'next' and 'previous' links to navigate though all the
     previews of the collection.

It parses and renders blog entries that have a ``.port`` file extension. The
Portico blog entry file format is different from most other Pyblosxom entry
types in that it follows the simple '.ini' style syntax.

Each entry file is required to have one section called ``entry``, with one
required 'option', called ``title``. Example::

  [entry]
  title: A small photographic report on my visit to Timbooktoo

The ``entry`` section recognizes two other options: ``thumbnails`` and
``cherries``. The first depicts the number of thumbnails to display whenever
the entry is not rendered at its permanent URL. The ``cherries`` option allows
to specify what thumbnails to show in a space seperated list of thumbnail
numbers.

Every image in the gallery has its own section in the file. Each of these
sections requires two 'options', ``image`` and ``thumbnail``. Example::

  [photo_1]
  image: http://foo.bar.com/path/to/image.jpg
  thumbnail: http://foo.bar.com/path/to/thumbnail.jpg

The displayed images are sorted on the section's title. At the current stage,
the section's title is not displayed. This may change. See also `TODO.txt`_

.. _`TODO.txt`: TODO

Portico will not create thumbnails nor preview nor resized versions of the
photos for you. At least not this moment. Who knows.. maybe it will at a later
stage.

Portico is at an early stage of development. It most probably still
contains bug here and there and its functionality might not suite anyone at
all. Feel free to send questions, ideas, patches or any other feedback to
``jw at n--tree dot net``.

How should it be used?
----------------------

There're at least two ways to install the Portico plugin:

  1) Copy (or link) the ``portico.py`` module in the ``plugins`` directory
     of your Pyblosxom installation

  2) adjust the ``py['plugins_dir']`` configuration option in the
     ``config.py`` file of your Pyblosom installation to include the
     directory containing the ``portico.py`` module.

If you're using the ``py['load_plugins']`` configuration option, you
probably know that in order for the Portico plugin to be usable, it needs to
be listed there.

After installation, you can start to write blog entries with the ``.port`` file
extension. Apart from being photo galleries and the specific file format used,
Portico entries behave like any other blog entry type.

What configuration options are available?
-----------------------------------------

There're currently six configuration options recognised by the plugin:

  ``py['portico_thumbs']``
    To set the number of thumbnails display, whenever the entry is not
    rendered at ot permanent URL. This number will be overrided whenever an
    individual entry has the ``thumbnails`` or ``cherries`` metadata field set.

  ``py['portico_single_image_template']``
    The template used for rendering one individual image. The following four
    variables are recognized for interpolation: ``prevlink`` (the URL to the
    previous image in the gallery, or an empty string if we're at the the
    first), ``nextlink`` (the URL to the next image in the gallery or an empty
    string if we're at the last), ``backlink`` (the permanent URL of the entry)
    and ``imagesrc`` (the URL for the image being displayed).

  ``py[''portico_gallery_main_template']``
    The template used to render the entry displaying the thumbnails in the
    gallery. There's two variables that are used for interpolation:
    ``thumbnails``, used to interpolate the sequence of thumbnails and
    ``morelink`` that is interpolated with the result of the
    ``portico_more_thumbnail`` template.

  ``py['portico_more_template']``
    The template used for the more link. There's one variable used for
    interpolation: ``morelink``, which is the permanent URL for the gallery
    entry.

  ``py['portico_thumbnail_template']``
    The template used for rendering one thumbnail (and thus is repeated for
    each of the thumbnails in the sequence). There's two variables used:
    ``singleimagelink`` and ``imagesrc``. The former is the URL that will
    render the single resized image. The latter is the URL for the thumbnail.

  ``py['portico_url_mapper']``
    Either an (importable) name or the factory function for a URL mapper.

The optional, pluggable URL mappers are used to determine the URL to the
thumbnails and resized versions of the images referenced in the ``.port`` file.
If there's a mapper configured, the thumbnail key in the image sections in the
``.port`` file is ignored. Instead, the image key is used and passed as an
argument to the ``thumbnail()`` and ``image()`` methods of the URL mapper.
These methods should return a URL.

The ``portico.py`` plugin module contains an example of a simple mapper
implementation. The ``image()`` method will just return the URL unmodified. The
``thumbnail()`` method will replace any occurence of ``resized`` in the URL
with ``thumbnails``. This mapper is compatible with the galleries generated by
the `gallery2.py`_ script.

.. _`gallery2.py`: http://www.net-es.dk/~pj/python/

What could it look like?
------------------------

You can see Portico in action in `the author's blog`_.

.. _`the author's blog`: http://jw.n--tree.net/blog/tools/portico

See also:
---------

  * The author's blog_

  .. _blog: http://jw.n--tree.net/tools/portico/

  * The `TODO.rst`_.

  .. _`TODO.rst`: TODO

  * The `portico.py`_ python module. It contains some smaller explanations
    and of course the plugin source code itself.

  .. _`portico.py`: portico

  * For the latest development version, check the Subversion repository_.

  .. _repository: http://svn.n--tree.net/portico/
