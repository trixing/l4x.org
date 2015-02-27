"""Simple pyblosxom gallery plugin, relies on filekicker for serving

(c) 2015 Jan Dittmer <jdi@l4x.org>
"""

import glob
import os
import re

KEYWORD = r'GALLERY:([^ ]+):'


def cb_postformat(args):
    request = args['request']
    config = request.getConfiguration()
    body = args['entry_data']['body']
    m = re.search(KEYWORD, body)
    if not m:
        return args['entry_data']
    filenames = m.group(1).split(',')
    datadir = config['datadir']
    assert datadir[-1] != '/'
    pics = sum([glob.glob(os.path.join(datadir, filename))
                for filename in filenames], [])
    content = '\n'.join([
        '<a href="%(link)s"><img src="%(link)s?small" alt="%(alt)s"></a>' % dict(
            link=pic.replace(datadir, ''),
            alt=os.path.basename(pic))
        for pic in pics])
    content = '<p class="gallery">\n%s</p>' % content
    args['entry_data']['body'] = re.sub(KEYWORD, content, body)
    return args['entry_data']
