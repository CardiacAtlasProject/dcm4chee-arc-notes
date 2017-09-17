#!/usr/bin/env bash

# prepare necessary packages
sudo yum -y install epel-release vim wget
sudo yum -y update
sudo yum -y groupinstall "Development tools"

# install JDK 1.8
sudo yum -y install java-1.8.0-openjdk-devel
sudo echo -e "export JAVA_HOME=/etc/alternatives/java_sdk_1.8.0" >  /etc/profile.d/jdk1.8.0.sh

# installing maven 3.3.9
if hash mvn 2>/dev/null; then
    echo "Package mvn has already been installed"
else

    mvnver="3.3.9"
    distfile="apache-maven-${mvnver}"
    url="http://www-eu.apache.org/dist/maven/maven-3/${mvnver}/binaries/${distfile}-bin.tar.gz"

    echo "DOWNLOAD & INSTALLING MAVEN version: ${mvnver}"

    $(curl -sS -o /tmp/${distfile}-bin.tar.gz ${url})
    $(sudo tar -C /opt -xzf /tmp/${distfile}-bin.tar.gz)
    $(rm -rf /tmp/${distfile}-bin.tar.gz)

    sudo echo -e "export PATH=\$PATH:/opt/${distfile}/bin"  > /etc/profile.d/mvn.sh
fi

# installing mysql server 5.7
if hash mysql 2>/dev/null; then
  echo "Package mysql has already been installed"
else

  echo "INSTALLING MYSQL 5.7"
  wget https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
  sudo rpm -ivh mysql57-community-release-el7-11.noarch.rpm
  sudo yum -y install mysql-server
  sudo systemctl start mysqld
  sudo systemctl status mysqld

fi

# installing openldap server
if hash slapd 2>/dev/null; then
  echo "Package openldap has already been installed"
else

  echo "INSTALLING OPENLDAP SERVER"

  sudo yum -y install openldap compat-openldap openldap-clients openldap-servers openldap-servers-sql openldap-devel
  sudo cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG
  sudo chown -R ldap:ldap /var/lib/ldap/

  sudo systemctl start slapd.service
  sudo systemctl enable slapd.service
  sudo systemctl status slapd.service

fi

# install pip & necessary modules
if hash pip 2>/dev/null; then
   echo "Package pip has already been installed"
else

  sudo yum -y install python-pip python-wheel
  sudo yum upgrade python-setuptools
  sudo pip install --upgrade pip
  sudo pip install docopt

  wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.7-1.el7.x86_64.rpm
  sudo rpm -ivh mysql-connector-python-2.1.7-1.el7.x86_64.rpm

fi
