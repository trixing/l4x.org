import pysvn, os, sys, anydbm, re, datetime, time

from config import py
from syslog import syslog

#py = {}
#py['blog_title'] = 'test'

def get_mtime(fname):
        cache_fname = os.path.join('/tmp/', py["blog_title"] + '-SVNDATES')
	try:
        	cache = anydbm.open(cache_fname, "c")
	except:
		return -1
	d = -1

        if True and cache.has_key(fname):
                d = float(cache[fname])
        else:
		p = os.popen("/usr/bin/svn --username=www --password=www-ro --non-interactive log -q  \"%s\" 2>/dev/null"%(fname),"r")
		s = p.read()
		p.close()
		syslog(s)
		sd = re.findall(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})',s)
		if sd:
			sd = sd[len(sd)-1]
			syslog("test %d"%(len(sd)))
			dt = datetime.datetime(int(sd[0]),int(sd[1]),int(sd[2]),int(sd[3]),int(sd[4]),int(sd[5]))
			d = time.mktime(dt.timetuple())
			syslog(fname + ' ' + str(dt))
                cache[fname] = str(d)

	#	try:
	#		client = pysvn.Client(fname)
	#		l = client.log(fname)
	#	except pysvn._pysvn.ClientError:
	#		l = []
	#		d = -1
#
#                if len(l) > 0:
#                        d = l[0]['date']
#			syslog(fname + ' ' + str(d))
#                        cache[fname] = str(d)
#                else:
#                        d = -1

#                del client

        del cache
        return d

def cb_filestat(args):
        d = get_mtime(args["filename"])
	args["mtime"] = list(args["mtime"])
        if d >= 0:
                args["mtime"][8] = d
        return args

#print get_mtime('../entries/imprint.txt')
