#!/bin/bash
echo "============================================================================"
echo "BEGIN MariaDB Server setup ....."

if [ ! -d "/etc/mysql" ] ; then
	mkdir -p /etc/mysql/conf.d/
	echo > /etc/mysql/conf.d/my.cnf <<EOF
[client]
default-character-set  = utf8

[mysqld]
bind-address           = 0.0.0.0
character-set-server   = utf8
collation-server       = utf8_general_ci
character_set_server   = utf8
collation_server       = utf8_general_ci
EOF
	apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xcbcb082a1bb943db
	add-apt-repository "deb http://mirrors.opencas.cn/mariadb/repo/10.1/ubuntu trusty main"
	apt-get update -qq

	echo > /tmp/selections <<EOF
# Repeat password for the MariaDB "root" user:
mariadb-server-10.1 mysql-server/root_password_again password root
# New password for the MariaDB "root" user:
mariadb-server-10.1 mysql-server/root_password password root
EOF
	debconf-set-selections /tmp/selections

	DEBIAN_FRONTEND=noninteractive aptitude install -q2 -y mariadb-server mariadb-client

	mysql -uroot <<-SQL
GRANT ALL PRIVILEGES ON *.* TO 'vagrant'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'vagrant'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SQL

fi


echo "END MariaDB Server setup ......"
echo "============================================================================"