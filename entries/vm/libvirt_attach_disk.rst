Attaching a new disk to a running VM

Just for my own memory (attaching 400G to vm named ``git0``::

  pool-create-as hdd --type dir --target /mnt/libvirt
  vol-create-as hdd gitdisk 400G --format qcow2
  attach-disk git0 /mnt/libvirt/gitdisk vdb

[[!meta date="2014-03-16 23:00:00"]]
