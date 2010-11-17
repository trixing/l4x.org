#!/bin/sh

for f in `find entries/ -type f -name '*.txt' -o -name '*.rst'`; do
	if ! test -f "$f"; then continue; fi
	echo $f
	DATE=$(svn info "$f" | egrep "^Last Changed Date" | cut -f4-5 -d' ')
	META="[[!meta date=\"$DATE\"]]"
	echo "$META" >> "$f"
done
