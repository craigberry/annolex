#!/bin/csh

###   Creates an empty annolex database.

$MYSQL_BIN/mysql -u $MYSQL_ROOT_USERNAME -p$MYSQL_ROOT_PASSWORD --batch --verbose <<eof
drop database if exists annolex;
create database annolex character set utf8;
grant all privileges on annolex.* to 'annolex'@'localhost' identified by 'annosql';
eof

