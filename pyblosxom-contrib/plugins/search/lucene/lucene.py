"""
Copyright (c) 2003-2005 Ted Leung

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
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Allow searching of the blog by using a Lucene search for a set of terms

To install:
 1) Put lucene.py in pyblosxom/Pyblosxom/plugins
 2) In config.py add lucene to py['load_plugins']
 3) Place the contents of pyblosxom/contrib/plugins/lucene/bin in a
    directory readable by pybloxsom.  In config.py, set py['lucene_bin'] to
    this path
 4) Download lucene from http://jakarta.apache.org/lucene and unzip/untar it.
    In config.py, set py['lucene_home'] to the lucene directory (which contains
    lucene-core-XX.jar and lucene-demos-XX.jar)
 5) In config.py set py['lucene_index'] to the name of the Lucene index file
    (pybosxom must be able to read and write this file)
 6) In config.py set py['lucene_highlight'] to True or False
 7) In config.py set py['JAVA_HOME'] to point at the 'java' command
 8) Set up a cron job to run py['lucene_bin']/index.sh periodically to
    reindex your blog
 9) Somewhere in your web page you need a lucene search form:

   <form id="searchform" method="get" action="/blog">
    <table>
     <tr>
      <td><input type="text" id="search" name="search" size="18" maxlength="255" value="" /></td>
      <td><input type="submit" value=Search /></td>
     </tr>
    </table>
   </form>

    The action of the form should be the top level URI of your blog

10) You should add $searchHeader somewhere in the header of your webpage; this
   is where statements like, "Your search returned X results for Y" are
   placed. This statement is enclosed in a div tag with a class of 
   "searchtext" so that you can define it as you like in your stylesheet.

11) You should add $searchHeader somewhere in the header of your webpage; this
    is where statements like, "Your search returned X results for Y" are
    placed. This statement is enclosed in a div tag with a class of
    "searchtext" so that you can define it as you like in your stylesheet.

"""

__author__ = "Ted Leung - twl@sauria.com"
__version__ = "$Id: lucene.py 1252 2008-07-04 03:44:59Z ryanbarrett $"

import glob, os, urllib, re
from Pyblosxom.entries import fileentry

def verify_installation(request):
    config = request.getConfiguration()

    retval = 1

    if not config.has_key('lucene_home') or not os.path.isdir(config['lucene_home']):
        print ('The "lucene_home" property in the config file must refer to '
               'a directory that contains the lucene libraries.')
        retval = 0

    if not config.has_key('JAVA_HOME') or not os.path.isfile(config['JAVA_HOME']):
        print ('The "JAVA_HOME" property in the config file must refer to '
               'the "java" command on your system.')
        retval = 0

    if not config.has_key('lucene_bin') or not os.path.isdir(config['lucene_bin']):
        print ('The "lucene_bin" property in the config file must refer to a '
               'directory that contains the lucene plugin scripts index.sh and '
               'search.sh.')
        retval = 0

    if not config.has_key('lucene_highlight'):
        print ('The "lucene_highlight" property in the config file must be '
               'set to either True or False')
        retval = 0

    return retval

def makeEntry(filename, request):
    """
    @param filename: filename of matching entry
    @type  filename: string
        
    @param request: the Request object
    @type  request: Request
    """
    config = request.getConfiguration()
    return fileentry.FileEntry(request, filename, config['datadir'])                                              
def search(request, config, term):
    """
    Search for the specified search term
    
    @param request: the Request object
    @type request:  Request

    @param config: a pyblosxom config dict
    @type config:  a dict
        
    @param term: the search term
    @type term: a string
    """
    urllib.quote(term)
    JAVA_HOME = config['JAVA_HOME']
    classpath = ':'.join(glob.glob(config['lucene_home'] + '/*.jar') +
                 [config['lucene_bin']])
    index = config['lucene_index']
    cmd = (JAVA_HOME + ' -cp ' + classpath + ' LuceneSearch ' + index + ' ' +
           term)
    pipe = os.popen(cmd, "r")
    results = pipe.readlines()
    status = pipe.close()
    results = [ os.path.join(config['datadir'], x[2:-1]) for x in results ]
    entries = [ makeEntry(x, request) for x in results ]
    entries = [ ( x._mtime, x ) for x in entries ]
    entries.sort()
    entries.reverse()
    return [ x[1] for x in entries ]

def cb_prepare(args):
    """
    Add a nice header for the Lucene search, this header
    goes into the $searchHeader variable for including in
    the header template file.
    """
    # do nothing if the form is not a lucene form
    request = args["request"]
    form = request.getHttp()['form']
    if not form.has_key("search"):
        return None
                                                                                
    data = request.getData()
    resultnumber = len(data['luceneResults'])

    if resultnumber < 1:
        data['searchHeader'] = ("<div class=\"searchtext\">Your search "
            "returned no results. Maybe I just never talk about <b>"
            + form["search"].value + "</b></div>")
    else:
        data['searchHeader'] = ("<div class=\"searchtext\">Your search "
            "returned " + str(resultnumber) + " results for <b>"
            + form["search"].value + "</b>:</div>")

def cb_filelist(args):
    """
    Lucene search handling
    """
    # do nothing if the form is not a lucene form
    request = args["request"]
    form = request.getHttp()['form']
    if not form.has_key("search"):
        return None
  
    config = request.getConfiguration()
    data = request.getData()
    
    data['luceneResults'] = search(request, config, form["search"].value)
    return data['luceneResults']

def cb_postformat(args):
    """
    Highlight matches if lucene_highlight is set to True in config.py
    """
    # do nothing if the form is not a lucene form
    request = args["request"]
    form = request.getHttp()["form"]
    if not "search" in form:
        return None

    # do nothing if highlighting is not enabled
    config = request.getConfiguration()
    if not config.get("lucene_highlight", False):
        return None

    title = args["entry_data"]["title"]
    body = args["entry_data"]["body"]

    term = form["search"].value
    term = re.sub('\*', '\w*', term)
    term = re.sub('\?', '\w', term)
    pattern = re.compile('\\b' + term + '\\b', re.IGNORECASE)
    args["entry_data"]["title"] = (pattern.sub(lambda match:
        "<span style='color:black;background-color:#ffff66'>"
        + match.group() + "</span>", title))
    args["entry_data"]["body"] = (pattern.sub(lambda match:
        "<span style='color:black;background-color:#ffff66'>"
        + match.group() + "</span>", body))
    return args["entry_data"]
