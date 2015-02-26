"""Simple pyblosxom gallery plugin, relies on filekicker for serving

(c) 2015 Jan Dittmer <jdi@l4x.org>
"""

import glob
import os
import re

KEYWORD = r'GALLERY:([^ ]+):'

def cb_filestat(args):
    print 'filestat', args
    return args

def cb_postformat(args):
    body = args['entry_data']['body']
    m = re.search(KEYWORD, body)
    if not m:
        return args['entry_data']
    dirnames = m.group(1).split(',')
    datadir = 'entries/'
    pics = sum([glob.glob(os.path.join(datadir, dirname))
                for dirname in dirnames], [])
    content = '\n'.join([
        '<a href="/%s"><img src="/%s" alt="%s"></a>' % (
            pic.replace(datadir, ''),
            pic.replace(datadir, '') + '?small',
            os.path.basename(pic))
        for pic in pics])
    content = '<p class="gallery">\n%s</p>' % content
    args['entry_data']['body'] = re.sub(KEYWORD, content, body)
    return args['entry_data']
