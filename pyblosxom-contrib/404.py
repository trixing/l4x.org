#!/usr/bin/python
"""
404.py
http://pyblosxom.sf.net/
Ryan Barrett <pyblosxom@ryanb.org>

This plugin displays the user template '404' on 404 not found errors. It
includes the $path, $path_stripped, and $title template variables, as well as
the variables from config.py, to allow for dynamic 404 handler templates.

VERSION:
0.2 Added to pyblosxom contrib pack
0.1 First release

Copyright 2006-2007 Ryan Barrett

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import re

__author__ = 'Ryan Barrett'
__version__ = '0.2'
__url__ = 'http://pyblosxom.sf.net/'
__description__ = 'Displays a user-provided template on 404 not found errors.'

def verify_installation(request):
  return 1

# TODO(ryanb): using the cb_logrequest() callback to catch 404s is a horrible
# hack. it'd be nice to have a callback for handling non-2xx response codes.
def cb_logrequest(args):
  request = args['request']
  config = request.getConfiguration()
  http = request.getHttp()
  response = request.getResponse()
  data = request.getData()
  renderer = data['renderer']

  if args['return_code'] == '404':
    renderer.flavour = renderer._getflavour(data.get('flavour', 'html'))

    if '404' in renderer.flavour:
      renderer.showHeaders()

      variables = dict(config)
      variables['path'] = http['PATH_INFO']
      variables['path_stripped'] = re.sub('[/_+?.=&#-]', ' ', http['PATH_INFO'])
      variables['title'] = '404 Not Found'

      renderer.setContent({ 'body': renderer.flavour['404'] % variables })

  return None
