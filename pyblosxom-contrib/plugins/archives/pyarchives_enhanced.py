"""
Walks through your blog root and generates yearly and monthly archives from all
available entries.  The generated html information is stored in the
$archivelinks variable which you can use in your head or foot templates.

You can format the output by setting these variables in your config.py:
"archives_start",
"archive_template_year",
"archive_template_month",
"archive_template_post" and
"archives_finish" .

"archives_start" starts the archive listing and is only used at the very
beginning. The "archive_template_year" and "archive_template_month" properties
are the templates for each year or rather month item. "archive_template_post"
represents a single post. Then, after all the
archives are printed, "archives_finish" ends the archives listing.

A config.py example:

py['archives_start'] = '<ul id="archives"><li>'

py['archive_template_year'] = '<div class="archiveYear"><a href="%(base_url)s/%(Y)s">%(Y)s</a> (%(c)s)</div>'

py['archive_template_month'] = '<div class="archiveMonth"><a href="%(base_url)s/%(Y)s/%(m)s">%(B)s %(Y)s</a> (%(c)s)</div>'

py['archive_template_post'] = '<div class="archivePost"><a href="%(base_url)s/%(post)s">%(title)s</a> </div>'

py['archives_finish'] = '</li></ul>'

The vars available through this plugin with typical example values are:
    b      'Jun'
    B      'June'
    m      '6'
    Y      '1978'
    y      '78'
    c      '(7)'
where "%(c)s" is the number of blog entries in a particular archive.

Available CSS elements:
    #archives
    .closed
    .open
    .clicker
    .archiveYear
    .archiveMonth
    .archivePost

CSS example:
#archives {
}
.closed {
  background: url(/images/closed.png) left center no-repeat;
}
.open {
  background: url(/images/opened.png) left center no-repeat;
}
.clicker {
  cursor: pointer;
}
.archiveYear {
  text-indent: 1.5em;
  margin: 5px 0px 2px 0px;
}
.archiveMonth {
  text-indent: 2em;
}
.archivePost {
  text-indent: 2.5em;
  font-size : 0.9em;
  margin: 2px 0px;
}

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Copyright 2004, 2005 Wari Wahab, 2008 Klaus Trainer
"""
__author__ = ["Wari Wahab - wari at wari dot per dot sg",
              "Klaus Trainer - klaus.trainer at web dot de"]
__version__ = "$Id$"
__url__ = "http://pyblosxom.sourceforge.net"
__description__ = "Creates yearly and monthly archives for PyBlosxom."

from Pyblosxom import tools
import re, time, os, os.path

def verify_installation(request):
    config = request.getConfiguration()
    if not config.has_key("archives_start"):
        print "Missing optional config property 'archives_start' which "
        print "allows you to specify how the archive links are created.\n"
        print "Refer to pyarchive plugin documentation for more details."
    if not config.has_key("archive_template_year"):
        print "Missing optional config property 'archive_template_year' which "
        print "allows you to specify how the archive links are created.\n"
        print "Refer to pyarchive plugin documentation for more details."
    if not config.has_key("archive_template_month"):
        print "Missing optional config property 'archive_template_month' which"
        print " allows you to specify how the archive links are created.\n"
        print "Refer to pyarchive plugin documentation for more details."
    if not config.has_key("archives_template_post"):
        print "Missing optional config property 'archives_template_post' which"
        print " allows you to specify how the archive links are created.\n"
        print "Refer to pyarchive plugin documentation for more details."
    if not config.has_key("archives_finish"):
        print "Missing optional config property 'archives_finish' which "
        print "allows you to specify how the archive links are created.\n"
        print "Refer to pyarchive plugin documentation for more details."
    return 1

class Record:
    def __init__(self, repr):
        self.count = 0
        self.archives = {}
        self.repr = repr

class PyblArchives:
    def __init__(self, request):
        self._request = request
        self._archives = None

    def __str__(self):
        if self._archives == None:
            self.genLinearArchive()
        return self._archives

    def genLinearArchive(self):
        config = self._request.getConfiguration()
        root = config["datadir"]
        year_archives = {}
        archiveList = tools.Walk(self._request, root)
        fulldict = {}
        fulldict.update(config)

        year_template = (config.get('archive_template_year',
            '<div class="archiveYear"><a href="%(base_url)s/%(Y)s">%(Y)s</a> (%(c)s)</div>'))
        month_template = (config.get('archive_template_month',
            '<div class="archiveMonth"><a href="%(base_url)s/%(Y)s/%(m)s">%(B)s %(Y)s</a> (%(c)s)</div>'))
        post_template = (config.get('archive_template_post',
            '<div class="archivePost"><a href="%(base_url)s/%(post)s">%(title)s</a> </div>'))

        for mem in archiveList:
            timetuple = tools.filestat(self._request, mem)
            timedict = {}
            # "%(c)d" will be correctly replaced
            # later by the number of archive entries...
            timedict["c"] = "%(c)d"
            for x in ["B", "b", "m", "Y", "y", "d", "H", "M", "S"]:
                timedict[x] = time.strftime("%" + x, timetuple)
            fulldict.update(timedict)

            # Create year entry if needed, and update count
            if not year_archives.has_key(timedict['Y']):
                year_archives[timedict['Y']] = Record(year_template % fulldict)

            year_entry = year_archives[timedict['Y']]
            year_entry.count += 1

            # Create month entry if needed, update count
            month_archives = year_entry.archives

            if not month_archives.has_key(timedict['m']):
                month_archives[timedict['m']] = Record(month_template % fulldict)

            month_entry = month_archives[timedict['m']]
            month_entry.count += 1

            # Save title of the post
            post_archives = month_entry.archives
            text = open(mem).readline()
            title = re.match(".+", text).group()
            post = os.path.basename(mem)
            fulldict.update({ 'title' : title, 'post' : post})
            post_archives[timedict['d'] + timedict['H'] + timedict['M'] + timedict['S']] = post_template % fulldict

        year_keys = year_archives.keys()
        year_keys.sort()
        year_keys.reverse()

        # Generate output
        result = [ config.get('archives_start', '<ul id="archives"><li>') ]
        for year_key in year_keys:

            year_entry = year_archives[year_key]

            result.append(year_entry.repr % {"c": year_entry.count})
            result.append('<div>')

            month_keys = year_entry.archives.keys()
            month_keys.sort()
            month_keys.reverse()

            for month_key in month_keys:

                month_entry = year_entry.archives[month_key]
                result.append(month_entry.repr % {"c": month_entry.count})
                result.append('<div>')

                post_keys = month_entry.archives.keys()
                post_keys.sort()
                post_keys.reverse()

                for post_key in post_keys:

                    post_entry = month_entry.archives[post_key]
                    result.append(post_entry)

                result.append('</div>')
            result.append('</div>')

        result.append(config.get('archives_finish', '</li></ul>'))
        self._archives = '\n'.join(result)

def cb_prepare(args):
    request = args["request"]
    data = request.getData()
    data["archivelinks"] = PyblArchives(request)
