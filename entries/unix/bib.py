"""
Requires the python-bibtex module from pybliographer

Example CSS style:

ul.bibtex span { color: #555; }
ul.bibtex .title { color:#000; }
ul.bibtex .author { font-style:italic; }
ul.bibtex .journal { font-style:italic; }
ul.bibtex .journal:after { content:","; }
ul.bibtex .volume:before { content:"Vol."; }
ul.bibtex .volume:after { content:","; }
ul.bibtex .number:before { content:"No."; }
ul.bibtex .number:after { content:","; }
ul.bibtex .pages:before { content:"pp. "; }
ul.bibtex .pages:after { content:","; }
ul.bibtex .year:after { content:""; }

Copyright (c) 2010 Jan Dittmer <jdi@l4x.org>

The MIT License (http://www.opensource.org/licenses/mit-license.php)

Copyright (c) 2003-2006 Wari Wahab
Copyright (c) 2003-2010 Will Kahn-Greene

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__version__ = '1'
__author__ = 'Jan Dittmer <jdi@l4x.org>'

from docutils.core import publish_parts
from Pyblosxom import tools
from urllib import quote_plus,quote

PREFORMATTER_ID = 'BibTex'
FILE_EXT = 'bib'

def cb_entryparser(args):
    args[FILE_EXT] = readfile
    return args

def cb_preformat(args):
    if args.get("parser", None) == PREFORMATTER_ID:
        return parse(''.join(args['story']), args['request'])

def read_bibtex(content,typemap={}):
    import _bibtex
    def expand(file,entry):
       items = entry[4]
       for k in items.keys():
           items[k] = _bibtex.expand (file, items [k], typemap.get (k, -1))
       items['key'] = entry[0]
       items['type'] = entry[1]
       return items

    file   = _bibtex.open_string("/dev/null", content, 0)

    entries = []
    while True:
        try:
            entry = _bibtex.next (file)

            if entry is None: break
            e = expand (file, entry)
            entries.append(e)
        except IOError, msg:
            pass
    return entries

def cmp(a,b):
    def key(e):
        l = 'Unknown Author'
        if e.has_key('author'):
          if len(e['author']) > 3:
            a = e['author'][3][0]
            if a[2] and a[1]:
                l = a[2]
            elif a[1]:
                l = a[1]
          else:
             l = str(e['author'][2])
         
        if e.has_key('year'):
            k = e['year'][2]
        else:
            k = '1980'
        return l + k
    ka = key(a)
    kb = key(b)
    if ka > kb:
        return 1
    elif ka < kb:
        return -1
    else:
        return 0


def parse(story, request):
    entries = read_bibtex(story)
    entries.sort(cmp)
    title = None
    ru = '<ul class="bibtex">\n'
    for e in entries:
        if e['type'] == 'title':
            title = e['title'][2]
            continue
        r = '  <li>\n'
        r += '    <span class="author">\n'
        l = []
        if e.has_key('author'):
          if len(e['author']) > 3:
            for a in e['author'][3]:
                if a[2] and a[1]:
                    l.append(a[1][0] + '. ' + a[2])
                elif a[1]:
                    l.append(a[1])
          else:
             l.append(str(e['author'][2]))
        else:
          l = ['']
        r += ', '.join(l)
        r += '</span> \n'
        if e.has_key('title') and len(e['title']) > 2:
            r += '    <span class="title">' + e['title'][2] + '</span> '
        if e.has_key('journal'):
            r += '    <span class="journal">' + e['journal'][2] + '</span> '
        elif e.has_key('booktitle'):
            r += '    <span class="journal">' + e['booktitle'][2] + '</span> '
        if e.has_key('volume'):
            r += '    <span class="volume">' + e['volume'][2] + '</span>'
        if e.has_key('number'):
            r += '    <span class="number">' + e['number'][2] + '</span>'
        if e.has_key('pages'):
            p = e['pages'][2].replace('--','-').replace(' ','')
            r += '    <span class="pages">' + p + '</span>'
        if e.has_key('year'):
            r += '    <span class="year">' + e['year'][2] + '</span>'
        if e.has_key('url'):
            r += '    <a class="url" target="_blank" href="'+e['url'][2]+'">URL</a>'
        if e.has_key('doi'):
            d = e['doi'][2].replace('DOI: ','').replace(' ','')
            r += '    <a class="doi" target="_blank" href="http://dx.doi.org/'+quote(d)+'">DOI</a>'
        if not e.has_key('url') and not e.has_key('doi') and e.has_key('title'):
            r += '    <a class="search" target="_blank" href="http://scholar.google.com/scholar?q='+quote_plus(e['title'][2])+'">Search</a>'
        r += '</li>\n'
        try: # try to use unicode first for entries.
            r = r.decode('utf-8').encode('iso8859-15')
        except UnicodeError:
            pass

        ru += r

    ru += '</ul>\n'
    return ru.decode('iso8859-15').encode('utf-8'),title

def readfile(filename, request):
    entryData = {}
    lines = open(filename).readlines()

    if len(lines) == 0:
        return {"title": "", "body": ""}


    body,title = parse(''.join(lines), request)
    if not title:
        import os.path
        title = os.path.basename(filename).replace('.bib','')
    entryData["title"] = title
    entryData["body"] = body

    tools.run_callback('postformat', {'request': request,
                                      'entry_data': entryData})
    return entryData
