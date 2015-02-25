How to securely bridge multiple libvirt networks using openswan

I own multiple root servers distributed in different data centers across
the world.  Each server runs libvirt and serves multiple VMs in private
subnets.  The goal of this exercise is to have the virtual machines
be able to securely talk to each other.  The default configuration for
libvirt enables NAT from a private network (192.168.122.0/24) to the Internet.

This post describes step-by-step how to establish secure tunnels between
three hosts (called b0, c0 and d0 respectively) but could very well be
extended further.  It enables hosting root servers in multiple heterogeneous
data centers and not worry about traffic between VMs.  They will be able to communicate with each other securely, just
like being on one single trusted router.

To establish the secure connection openswan is used
and the following instructions assume and are tested with Debian/wheezy.
Openswan as of writing this is at version 2.6.37-3 and libvirt is at 0.9.12-11.  No further packages
should be necessary (``apt-get install openswan libvirt-bin``).

First of all different subnets need to be assigned to each host.  For this
use ``virsh net-edit default`` and change any occurrence of 192.168.122 by
a unique number.  The following is my own configuration used for the further examples::

  Host  Public-IP  Subnet
  ----  ---------  ----------------
  b0    10.2.2.2   192.168.122.0/24
  c0    10.3.3.3   192.168.123.0/24
  d0    10.4.4.4   192.168.124.0/24

Next restart ``libvirt`` and verify using ``ifconfig``/``ip`` that the configuration has been
applied.  If any VM had a static IP address assigned it might need to be changed.

In the next step ipsec needs to be configured on each host.  Open ``/etc/ipsec.conf`` in your
favorite editor
and add the following lines for each pair of hosts needing to directly communicate
with each other::

  conn b0-to-c0
   authby=secret
   auto=start
   type=tunnel
   left=10.2.2.2
   leftid=10.2.2.2
   leftsubnet=192.168.122.0/24
   right=10.3.3.3
   rightid=10.3.3.3
   rightsubnet=192.168.123.0/24

  conn b0-to-d0
   ...
   left=10.2.2.2
   leftsubnet=192.168.122.0/24
   ...
   right=10.4.4.4
   rightsubnet=192.168.124.0/24
   ...

  conn c0-to-d0
   ...
   left=10.3.3.3
   leftsubnet=192.168.123.0/24
   ...
   right=10.4.4.4
   rightsubnet=192.168.124.0/24
   ...

The same file can be used for every host because non-existing interfaces will just
be ignored.  The left/right designation is arbitrary.

If multiple gateways exist on the host, the following might be useful (in addition to a ``listen 10.2.2.2`` in the ``config setup`` section)::

 leftnexthop=10.2.2.4

Next up configure authentication tokens between the hosts.  It is recommended to use host keys for
the connection, but for the sake of simplicity this uses the same
preshared key between all hosts (DO NOT DO THIS IN PRODUCTION).
Edit ``/etc/ipsec.secrets`` and add::

  10.2.2.2 %any: "s3cr3t"
  10.3.3.3 %any: "s3cr3t"
  10.4.4.4 %any: "s3cr3t"

Restart ipsec (``/etc/init.d/ipsec restart``) on both ends.  Execute
``ipsec auto --up b0-to-c0`` on each side and use ``ipsec look`` and
``/var/log/daemon.log`` to verify that the tunnel comes up.

In theory it should be possible to ping both ends of the tunnel.  But
libvirt installs a pesky NAT rule by default to circumvent this execute
the following (can go into ``/etc/rc.local``)::

  iptables -I POSTROUTING 1 -d 192.168.0.0/16 -j RETURN  -t nat

This effectively disables the NAT rules for the whole private subnet
starting with 192.168.  Now try::

  ping -I 192.168.123.1 192.168.122.1

If it does not work see above how
to verify that the tunnel came up.  If this is inconclusive
``tcpdump 'udp port 500'`` and on port 4500 should show in- and outgoing
packets.  Verify that all IP addresses are correct and no other firewall
rules are blocking communication on these ports.

It is necessary to specify ``-I 192.168.123.1`` for ping because ipsec
doesn't install a default route for the network connection (different protocol
layer).  Thus execute a final::

  route add -net 192.168.0.0/16 virbr0

on the host to route any traffic to and from the virtual machines correctly.  Now
``ping`` should work without the ``-I`` parameter.  Make it permanent by
adding it to ``/etc/rc.local``.

Communicating from within the VMs should now just work.  Verify that pinging
around different network produces the desired results.  If not verify that
IP forwarding is actually enabled.  ``/etc/sysctl.conf`` should contain the
following line::

  net.ipv4.ip_forward=1

As always with security, cross check this against other documentation and
verify using ``tcpdump`` etc.  that the traffic is actually encrypted.

[[!meta date="2014-02-02 16:00:00"]]
