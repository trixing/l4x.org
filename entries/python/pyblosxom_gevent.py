"""
Simple wrapper to start pyblosxom under gevent.

(c) 2014 Jan Dittmer <jdi@l4x.org>
"""
import argparse
import os
import sys
sys.path.insert(2, os.path.abspath(os.path.dirname(__file__)))
from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

from Pyblosxom import pyblosxom


def start(host='127.0.0.1', port=8007, threads=8):
    pool = Pool(threads)
    application = pyblosxom.PyblosxomWSGIApp()
    server = WSGIServer((host, port), application,
                        spawn=pool)#, log=None)
    server.serve_forever()


def main():
  p = argparse.ArgumentParser(description='Pyblosxom')
  p.add_argument('--port', dest='port', type=int, default=8007)
  p.add_argument('--host', dest='host', default='127.0.0.1')
  p.add_argument('--threads', dest='threads', type=int, default=8)
  args = p.parse_args()
  while True:
    try:
      start(args.host, args.port, args.threads)
    except KeyboardInterrupt:
      break
    except Exception as e:
      print 'Exception', str(e)


if __name__ == '__main__':
  main()
