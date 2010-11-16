#!/bin/sh

SVN="svn://svn.l4x.org/"

cd $HOME

test -d web || svn co $SVN/web/trunk web
test -d webroot || svn co $SVN/webroot/webroot/trunk webroot
test -d ctestng || svn co $SVN/ctest/ctestng ctestng

cd $HOME/web && svn up
cd $HOME/webroot && svn up
cd $HOME/ctestng && svn up

# as root...
if [ "$1" == "setup" ]; then
cd web
su root -c "cd /home/jdittmer/web/ ;
ln -s $PWD/apache/l4x.org.conf /etc/apache2/l4x.org.conf ;
ln -s $PWD/l4x.org/ssl /etc/apache2/starcom ;
ln -s $PWD/apache/l4xssl.conf /etc/apache2/sites-enabled/000-l4xssl ;
ln -s $PWD/apache/000-default /etc/apache2/sites-enabled/ ;
ln -s $PWD/apache/030-trixing /etc/apache2/sites-enabled/ ;
ln -s $PWD/apache/035-familiedittmer.de /etc/apache2/sites-enabled/ ;
ln -s $PWD/apache/040-l4xorg /etc/apache2/sites-enabled/  ;
apt-get install pyblosxom ;
rm /etc/pyblosxom/config.py ;
ln -s /home/jdittmer/web/l4x.org/config.py /etc/pyblosxom/config.py ;
a2enmod ssl;
apt-get install pyblosxom python-svn python-docutils php5 php5-pgsql \
	postgresql-8.3 postgresql-plperl-8.3 python-bibtex;
apache2ctl restart;
"


fi
