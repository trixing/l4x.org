#!/usr/bin/python
"""
filekicker.py
A pyblosxom plugin.

http://snarfed.org/space/filekicker
Copyright 2006 Ryan Barrett

This plugin serves static files in the pyblosxom datadir. It looks for the
filename from the URL based at datadir. For example, if config['datadir'] is
'/home/ryanb/www/data', and a user requests http://mysite.com/foo/bar.py,
filekicker will send back the file /home/ryanb/www/data/foo/bar.py. Its MIME
type is inferred from its extension.

In other words, filekicker takes a static file and "kicks" it up into the
pyblosxom structure.

Inspired by Magnus Nordlander's imagekicker plugin:
http://www.nordlander.tk/pyblosxom/

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""

__author__ = 'Ryan Barrett <pyblosxom at ryanb dot org>'
__version__ = '0.2'
__url__ = 'http://snarfed.org/space/filekicker'
__description__  = 'Serves static files through pyblosxom'

import mimetypes
import os
import os.path
import stat
import types

from PIL import Image,ImageOps,ImageDraw

# chunk size for transferring files
BLOCK_SIZE = 4096

# populate this with MIME types to replace with text/plain, for in-browser
# viewing.
REDUCE_TO_TEXT_PLAIN = ['text/python', 'text/x-python', 'text/lisp',
                        'text/elisp', 'text/x-diff']

EXTENSIONS = ('pdf', 'jpg', 'png', 'py', 'zip')

def verify_installation(request):
  # no setup necessary
  return True

def resize(name, dst, size=None):
        if not size:
            size = (256, 256)
        try:
          im = Image.open(name)

          if im.mode != "RGB" and im.mode != "RGBA":
            im = im.convert("RGB")

          im = ImageOps.fit(im, size, Image.ANTIALIAS, 0.01, (0.5,0.5,))
          im = ImageOps.autocontrast(im)
        except IOError:
            im = Image.new("RGB",size)
            draw = ImageDraw.Draw(im)
            draw.line( [0,0,] + size, fill=(255,0,0))
            draw.line( (0, size[1], size[0], 0), fill=(255,0,0))
            del draw

        im.save(dst,quality=80)
        del im
        return True


def cb_handle(args):
  request = args['request']
  config = request.getConfiguration()
  response = request.getResponse()

  # does the file exist?
  filename = request.getHttp()['PATH_INFO']
  filename = config['datadir'] + '/' + filename
  _, ext = os.path.splitext(filename)
  if ext[1:] not in EXTENSIONS:
        return
  if not os.path.isfile(filename):
    return

  qs = request.getHttp()['QUERY_STRING']
  # add the headers
  type, encoding = mimetypes.guess_type(filename)
  if type:
    if type in REDUCE_TO_TEXT_PLAIN:
      type = 'text/plain'
    if type in ('image/png', 'image/jpeg'):

      size = None
      if 'small' in qs:
        size = (150, 150)
      if 'x' in qs:
        size = [int(x) for x in qs.split('x')]
      if size:
        f = '%d_%d_' % size + filename.replace('/', '_')
        dst = os.path.join(config['imagedir'], f)
        try:
            os.makedirs(config['imagedir'])
        except os.error:
            pass
        resize(filename, dst, size)
        filename = dst
        type = 'image/png'
    response.addHeader('Content-Type', type)

  if encoding:
    response.addHeader('Content-Encoding', encoding)

  length = os.stat(filename)[stat.ST_SIZE]
  response.addHeader('Content-Length', str(length))

  # send the file to the client
  f = file(filename, 'rb', BLOCK_SIZE)
  while True:
    block = f.read(BLOCK_SIZE)
    if not block:
      break
    response.write(block)

  f.close()
  return 1
