Installing a StartSSL certificate with haproxy

`haproxy <http://www.haproxy.org>`_
since version 1.5 supports native SSL.  It uses a
combined PEM file for encrypting connections.

`StartSSL <https://www.startssl.com>`_ is
a popular provider of free SSL certificates (which I happen to use), but only
provides separate ``ssl.crt`` and ``ssl.key`` files.

To install these with *haproxy* they need to be combined into a single PEM file.
It is helpful to also present the intermediary certificates, which can
be downloaded on the StartSSL website as well. Otherwise clients might not
recognize the certificate as valid because they cannot verify the certificate
chain.

To combine them into one, ``cat`` works just fine:

  cat ssl.crt sub.class2.server.ca.pem ca.pem ssl.key > ssl.pem

Install it in *haproxy* by adding a bind option to the
``frontend`` block, e.g.

  bind :443 ssl crt /etc/haproxy/ssl.pem
  bind :::443 ssl crt /etc/haproxy/ssl.pem

This is what I'm running on `l4x.org <https://l4x.org>`_.

[[!meta date="2014-12-03 01:00:00"]]
