Pretty list of database and table sizes with PostgreSQL

A very handy way to estimate the on-disk size of your databases in
PostgreSQL:

::

    > SELECT datname,pg_size_pretty(pg_database_size(datname)) FROM pg_database;
        datname    | pg_size_pretty
    ---------------+----------------
     template1     | 4144 kB
     template0     | 4144 kB

And the same for individual tables:

::

    > SELECT tablename,pg_size_pretty(pg_total_relation_size(tablename)) 
        FROM pg_tables WHERE schemaname NOT IN ('information_schema','pg_catalog');

             tablename          | pg_size_pretty
    ----------------------------+----------------
     django_content_type        | 40 kB
     django_session             | 152 kB
     django_site                | 24 kB

Now go and bug your application developers to save your resources.
