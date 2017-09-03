This is a highly opinionated installation notes for unsecured dcm4chee-arc server.

Status: **working**

# I'm using ...

1. [Vagrant](https://www.vagrantup.com/) for the vm box.
2. [CentOS 7](https://www.centos.org/) for the vm engine.
3. [MySQL 5.7.19](https://www.mysql.com/) community edition for the pacs database.
4. [OpenLDAP](https://www.openldap.org/) server for the ldap server.
5. [Wildfly 10.1.0](http://wildfly.org/) for the application server.

# Setting up the vm

1. If you don't have **vagrant**, then install it first [from here](https://www.vagrantup.com/downloads.html).
   And also the plugins
   ```
   $ vagrant plugin install vagrant-vbguest
   ```

2. Create a directory for your vm.

3. Create **CentOS 7** vm:
   ```
   $ cd <DIRECTORY_FROM_STEP_2>
   $ wget https://raw.githubusercontent.com/avansp/dcm4chee-arc-notes/master/utils/vagrant-bootstrap.sh
   $ mkdir shared
   $ vagrant init centos/7
   ```

3. Edit `Vagrantfile` file and insert the following lines:
   ```
   # wildfly web access
   config.vm.network "forwarded_port", guest: 8080, host: 8080
   # mysql access
   config.vm.network "forwarded_port", guest: 3306, host: 3306
   # ldap access (note that the host uses 3890 for safety reason)
   config.vm.network "forwarded_port", guest: 389, host: 3890

   # share the shared folder
   config.vm.synced_folder "./shared", "/shared"

   # run provisioning script
   config.vm.provision :shell, path: "vagrant-bootstrap.sh"
   ```

4. Start up the vm engine, enter and update/install applications:
   ```
   $ vagrant up
   $ vagrant ssh
   [vagrant@localhost ~]$
   ```

You can transfer files between host and guest machines using `/shared` folder in the vm.

> From now on, all command line statements are made within the vagrant vm. I will just write it as `$` for brevity.

# Setting up the MySQL server

Lookup the default root password for mysql:
```
$ sudo grep 'temporary password' /var/log/mysqld.log
```

Change the default root password:
```
$ sudo mysql_secure_installation
```

# Setting up OpenLDAP server

```
$ sudo slappasswd
New password:
Re-enter new password:
SECRET_KEY
```

The root OpenLDAP password and the `SECRET_KEY` are going to be needed for later steps. So, I make references for this note as:
* **`$ROOT_OPENLDAP_PASSWD`** for the root password
* **`$SECRET_KEY_OPENLDAP`** for the SECRET_KEY generated from the last command above

# Installing dcm4chee-arc server

The installation process is pretty complicated. You can see the full details from the [dcm4chee-arc-light installation page](https://github.com/dcm4che/dcm4chee-arc-light/wiki/Installation). I have made a python script to automate the installation process.

First, we need to download a couple of things.

1. Download the `dcm4chee-arc` binary distribution
```
$ wget https://sourceforge.net/projects/dcm4che/files/dcm4chee-arc-light5/5.10.5/dcm4chee-arc-5.10.5-mysql.zip
$ unzip dcm4chee-arc-5.10.5-mysql.zip
```

2. Download the `wildfly` application server
```
$ wget -qO- http://download.jboss.org/wildfly/10.1.0.Final/wildfly-10.1.0.Final.tar.gz | tar xvz
```

3. Download the mySQL JDBC connector
```
$ wget -qO- https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.44.tar.gz | tar xvz
```

Create `dcm4chee-arc-config.json` file below to set user settings and permissions to the MySQL and OpenLDAP servers. Change the values according to your setup.
```json
{
  "dcm4cheeDir": "/home/vagrant/dcm4chee-arc-5.10.5-mysql",
  "wildflyHome": "/home/vagrant/wildfly-10.1.0.Final",
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "rootPasswd": "<ROOT_PASSWORD_TO_MYSQL_FROM_PREVIOUS_STEP>",
    "dbName": "<DCM4CHEE_PACS_DATABASE_NAME>",
    "userName": "<NEW_MYSQL_USER_TO_CONNECT_FROM_DCM4CHEE>",
    "userPasswd": "<SET_MYSQL_USER_PASSWORD>"
  },
  "ldap": {
    "rootPasswd": "<$ROOT_OPENLDAP_PASSWD>",
    "olcRootPW": "<$SECRET_KEY_OPENLDAP>",
    "domainName": "your-domain.org"
  },
  "jdbcJarFile" : "/home/vagrant/mysql-connector-java-5.1.44/mysql-connector-java-5.1.44-bin.jar"
}
```

Run the installation script:
```bash
$ wget https://raw.githubusercontent.com/avansp/dcm4chee-arc-notes/master/centos7-mysql/install-dcm4chee-arc-mysql.py
$ python install-dcm4chee-arc-mysql.py dcm4chee-arc-config.json
```

# Configure the WildFly

In the next step, you must run the dcm4chee-arc and apply the configuration steps below from another shell.

1. Start the `dcm4chee-arc`
   ```
   $ ~/wildfly-10.1.0.Final/bin/standalone.sh -b 0.0.0.0 -c dcm4chee-arc.xml
   ```
   Note the binding address `0.0.0.0` in order to accept webpage request from all sources.

2. Open a shell in another terminal.

   *You can open another shell by calling `vagrant ssh` again from your guest machine*

3. Configure the wildfly using another script:
   ```
   $ wget https://raw.githubusercontent.com/avansp/dcm4chee-arc-notes/master/centos7-mysql/configure-dcm4chee-arc.py
   $ python configure-dcm4chee-arc.py dcm4chee-arc-config.json
   ```  

4. Open the UI at http://localhost:8080/dcm4chee-arc/ui2


-----
**ENJOY!!**
