"""
(c) Jan Dittmer <jdi@l4x.org> 2015

A simple http server where any request triggers a git pull.
For use as github service hook.
"""
import argparse
from gevent import monkey; monkey.patch_all()
from gevent import pywsgi
import subprocess


def handler(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    output = subprocess.check_output(["/usr/bin/git", "pull"])
    yield output


def main():
  p = argparse.ArgumentParser(description='Updater')
  p.add_argument('--port', dest='port', type=int, default=8009)
  p.add_argument('--host', dest='host', default='127.0.0.1')
  args = p.parse_args()
  pywsgi.WSGIServer(
          (args.host, args.port), handler).serve_forever()


main()
