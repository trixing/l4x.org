import re, time
import re

DAYMATCH = re.compile('([0-9]{4})-([0-1][0-9])-([0-3][0-9])(.([0-2][0-9]):([0-5][0-9]):([0-5][0-9]))?')

def get_mtime(fname):
    f = file(fname,"r")
    c = f.read()
    mtch = DAYMATCH.search(c)
    mtime = None
    if mtch:
        try:
            year = int(mtch.group(1))
            mo = int(mtch.group(2))
            day = int(mtch.group(3))
            if mtch.group(4) is None:
                hr = 0
                minute = 0
            else:
                hr = int(mtch.group(5))
                minute = int(mtch.group(6))
            mtime = time.mktime((year,mo,day,hr,minute,0,0,0,-1))
        except Exception as e:
            print e
            # TODO: Some sort of debugging code here?
            pass

    return mtime

def cb_filestat(args):
        mtime = get_mtime(args["filename"])
	args["mtime"] = list(args["mtime"])
        if mtime >= 0:
                args["mtime"][8] = mtime
        return args

def cb_postformat(args):
	args['entry_data']['body'] = re.sub(r'\[\[(.*?)\]\]','',args['entry_data']['body'])
	return args['entry_data']
