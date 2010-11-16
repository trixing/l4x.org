"""
tags.py
Creates a tagging environment for pyblosxom

Tagging is like having an entry belong to multiple categories. For
example, an entry about Bike Riding in Pennsylvania can belong to
both Biking and Pennsylvania.

For more information on tags, please see sites such as technorati.com
and del.icio.us.

In your config file, create 4 settings:
py['tag_url']
py['pretext']
py['posttext']
py['tagsep']

The default tag_url should be set to http://yoursite/tags/, but you can also set 
it to something like http://technorati.com/tags/.  Please make sure to 
have the trailing slash.

The pretext and posttext will appear on your webpage surrounding your
tags and tagsep will note what to seperate the tags by.

So, for example, if I have 
py['pretext'] = '<span class="tags">Tags '
py['posttext'] = '</span>'
py['tagsep'] = ', '

Then it would appear like:

	<span class="tags">Tags: biking, pennsylvania</span>

Why not just put the text in a template? Because if you don't want to tag
an entry, this would look goofy:

	Tags: (nothing)

Finally, add a meta-data tag to your entries:
	
	#tags biking,pennsylvania
	
comma, no space.


If you choose to set your tag_url to
http://yoursite/tags/, you will be able to do a search 
for all tagged items like so:

	http://yoursite/tags/biking

Questions, comments, and fixes can be sent to joe@terrarum.net

** support for searching "untagged" tag hacked in by Timothy C. Fanelli - 10/22/05 **
	Tim made the following changes:
	It now filters out files that do not have a .txt extension -- this may
	or may not be generally desirable, as some other plugins allow
	different extensions for entries (e.g., portico looks for .port files,
	which might want to be tagged.)

	Also, I modified it to allow searching for "untagged" entries, using
	$tag_url/untagged -- it'l return entries which have no #tag meta
	entry. This was useful because I was completely replacing my
	categories with tags, and have a large "general" category which I
	didn't want to be bothered with.

        10/24 - 
           1.   Updated file filter hack to support config propery 'taggable_files'
                
                Set py[ 'taggable_files' ] = [ "txt", "port", ... ]
		To support tagging of entries with those file extensions. 
                Defaults to tag just entries with "txt" files.
                
           2.  cb_fileset now returns entries sorted by date with most current first.
"""

__author__ = 'Joe Topjian <joe@terrarum.net>'
__version__ = '200510242045 TCF'
__url__ = 'http://joe.terrarum.net'

# Variables

import os, re, sys

# Change this if your Pyblosxom installation is somewhere different!
from Pyblosxom import entries

def cb_filelist(args):
        request = args['request']
	config = request.getConfiguration()
        data = request.getData()
	new_files = [ ]

	tagfileswithext = [ "txt" ]
	if config.has_key( 'taggable_files' ):
		tagfileswithext = config[ 'taggable_files' ]

	ignore_directories = config['ignore_directories']

	m = re.compile(r'^%s' % config['tag_url']).match(data['url'])
	if m:
		tag = re.sub("%s" % config['tag_url'],'',data['url'])
		
		for root,dirs,files in os.walk(config['datadir']):
			for x in files:
				m = re.compile('.*\.([^.]+)$').search(x)
				if m and m.group(1) in tagfileswithext:
					entry_location = root + "/" + x 
					directory = os.path.dirname(entry_location)
					if ( os.path.split(directory)[1] in ignore_directories ):
						continue

					contents = open(entry_location,'r').read()

					m = re.compile('\n#tags\s+(.*)\n' ).search(contents)
					if ( m and tag in m.group(1).split(',') ) or ( not m and tag == 'untagged' ):
						tmpentry = entries.fileentry.FileEntry(request, entry_location, data['root_datadir'])
						new_files.append(( tmpentry._mtime, tmpentry ))


	if new_files:
		new_files.sort()
		new_files.reverse()

		myentries = []
		for myentry in new_files:
			myentries.append( myentry[1] )
		return myentries
	
def cb_story(args):
        request = args['request']
	config = request.getConfiguration()
	entry = args['entry']
	if entry.has_key('tags'):
		formatted_tags = [ ]
		temp_tags = [ ]
		formatted_tags.append(config['pretext'])
		tags = entry.getMetadata('tags').split(',')

		for tag in tags:
			temp_tags.append('<a href="%s%s" rel="tag">%s</a>' % (config['tag_url'], tag, tag))

		formatted_tags.append(config['tagsep'].join(temp_tags))
          	formatted_tags.append(config['posttext'])
		entry.setMetadata('tags',' '.join(formatted_tags))


