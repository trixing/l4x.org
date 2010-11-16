__author__ = 'Jan Dittmer <jdi@l4x.org>'
__version__ = '1'
__url__ = 'http://l4x.org'

from Pyblosxom import entries
import os,re

def cb_filelist(args):
        request = args['request']
	config = request.getConfiguration()
	pic_url = 'http://l4x.org/pics/'
	pic_dir = '/mnt/backup/pics/'
	if config.has_key('pic_url'):
		pic_url = config['pic_url']
	if config.has_key('pic_dir'):
		pic_dir = config['pic_dir']
        data = request.getData()
	new_files = [ ]
	#raise data['url']
	m = re.compile(r'^%s' % pic_url).match(data['url'])
	if not m:
		return
	dir = pic_dir + re.sub("%s" % pic_url,'',data['url'])
	for e in os.listdir(dir):
		entry_location = dir + e
		tmpentry = entries.fileentry.FileEntry(request, entry_location, data['root_datadir'])
		new_files.append(( tmpentry._mtime, tmpentry ))

	return new_files
 
