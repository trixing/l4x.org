Running Pyblosxom with gevent.wsgi

The `gevent wsgi server <http://www.gevent.org/gevent.wsgi.html>`_
is very easy to use from Python.  I wrote
a convenient wrapper which starts `pyblosxom <http://http://pyblosxom.github.io/>`_
under gevent.  This can be used to
either serve your blog locally for testing or to serve the live
system.  The nice thing is that it doesn't require an extra apache
or nginx server just to start serving it.

Full source code is located `here </python/pyblosxom_gevent.py>`_.

The important piece::

  from gevent import monkey; monkey.patch_all()
  from gevent.pool import Pool
  from gevent.pywsgi import WSGIServer
  from Pyblosxom import pyblosxom

  def start(host='127.0.0.1', port=8007, threads=8):
    pool = Pool(threads)
    application = pyblosxom.PyBlosxomWSGIApp()
    server = WSGIServer((host, port), application, spawn=pool)
    server.serve_forever()

[[!meta date="2014-06-03 23:00:00"]]
