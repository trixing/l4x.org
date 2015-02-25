ssh: Group readable id_rsa identity file

Let's say you want to use a system wide ssh identity file to access (or push)
shared server state from different users on the system.

The naive way is to ``chmod 0640 /system/wide/id_rsa``.  Only ssh will complain
loudly about that without a way to disable the error::

  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  Permissions 0640 for '/etc/git-readonly/id_rsa' are too open.
  It is recommended that your private key files are NOT accessible by others.
  This private key will be ignored.
  bad permissions: ignore key: /etc/git-readonly/id_rsa

The usual answer to this is that you do not do that.  Use different keys per
user or host based checking or an ssh-agent.

But lets say you really want to.  A viable workaround is to make a copy of the
file with the right permissions:

My ssh wrapper for this is::

  RSA=$HOME/.ssh/git-readonly-id_rsa
  cat /etc/git-readonly/id_rsa > "$RSA"
  chmod 0600 "$RSA"
  exec ssh  -o UserKnownHostsFile=/etc/git-readonly/known_hosts -o StrictHostKeyChecking=yes -i "$RSA" "$@"

Use at your own risk!


[[!meta date="2013-11-17 16:00:00"]]
