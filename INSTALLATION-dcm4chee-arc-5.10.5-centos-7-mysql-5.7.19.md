This is a highly opinionated installation notes for unsecured dcm4chee-arc server.

More installation details can be found from [dcm4chee-arc-light installation page](https://github.com/dcm4che/dcm4chee-arc-light/wiki/Installation).

Status: **working**

# I'm using ...

1. [Vagrant](https://www.vagrantup.com/) for the vm box.
2. [CentOS 7](https://www.centos.org/) for the vm engine.
3. [MySQL 5.7.19](https://www.mysql.com/) community edition for the pacs database.
4. [OpenLDAP](https://www.openldap.org/) server for the ldap server.
5. [Wildfly 10.1.0](http://wildfly.org/) for the application server.

# Setting up the vm

1. If you don't have **vagrant**, then install it first [from here](https://www.vagrantup.com/downloads.html).

2. Create **CentOS 7** vm:
   ```
   $ vagrant plugin install vagrant-vbguest
   $ vagrant init centos/7
   ```
   
3. Edit `Vagrantfile` file and insert the following lines for fowarding ports:
   ```
   # wildfly web access
   config.vm.network "forwarded_port", guest: 8080, host: 8080
   # mysql access
   config.vm.network "forwarded_port", guest: 3306, host: 3306
   # ldap access (note that the host uses 3890 for safety reason)
   config.vm.network "forwarded_port", guest: 389, host: 3890
   ```
   
4. Start up the vm engine, enter and update default applications:
   ```
   $ vagrant up
   $ vagrant ssh
   [vagrant@localhost ~]$ sudo yum update
   ```

The default shared folder is the `vagrant` that you can use for transfering files between guest and host machines.

> From now on, all command line statements are made within the vagrant vm. I will just write it as `$` for brevity.

# Setting up the MySQL server

```
$ sudo yum install -y wget
$ wget https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
$ sudo rpm -ivh mysql57-community-release-el7-11.noarch.rpm
$ sudo yum -y install mysql-server
$ sudo systemctl start mysqld
$ sudo systemctl status mysqld
```

You should see the status of **active (running)** on the output display.

Lookup the default root password for mysql:
```
$ sudo grep 'temporary password' /var/log/mysqld.log
```

Replace the root password:
```
$ sudo mysql_secure_installation
```

# Setting up OpenLDAP server
