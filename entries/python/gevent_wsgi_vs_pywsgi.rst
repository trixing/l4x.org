Python: gevent's WSGIServer, wsgi vs. pywsgi

The gevent wsgi server is one of the fastest out in the open.
I switched part of my applications to it and everything worked
fine after restarting the server and testing locally.  Unfortunately my
``haproxy`` frontend loadbalancer is not able to see the new backend
though.  Turns out that ``gevent.wsgi`` does not support HTTP 1.0 which
``haproxy`` uses for health checking.

The simple solution is to use ``gevent.pywsgi``.  This has some performance
penalty though.

An alternative might be (untested) to configure ``haproxy`` with HTTP 1.1
healthchecks::

  option httpchk OPTIONS / 1.1

[[!meta date="2013-11-16 16:00:00"]]
