import pysvn, os, sys, anydbm

from config import py

def get_mtime(fname):
        cache_fname = os.path.join(py['datadir'], 'SVNDATES')
        cache = anydbm.open(cache_fname, "c")

        if cache.has_key(fname):
                d = float(cache[fname])
        else:
                client = pysvn.Client(fname)
                l = client.log(fname)

                if len(l) > 0:
                        d = l[0]['date']
                        cache[fname] = str(d)
                else:
                        d = -1

                del client

        del cache
        return d

def cb_filestat(args):
        args["mtime"] = list(args["mtime"])
        d = get_mtime(args["filename"])
        if d >= 0:
                args["mtime"][8] = d
        return args

