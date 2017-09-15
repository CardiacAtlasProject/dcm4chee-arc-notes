This is a highly opinionated installation notes for **secured** dcm4chee-arc server.

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
   # dicom communication
   config.vm.network "forwarded_port", guest: 11112, host: 11112

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

# Configure WildFly

Full details are given in https://github.com/dcm4che/dcm4chee-arc-light/wiki/Installation-and-Configuration

Following instructions have been made easier for the settings above.

1. Download the `dcm4chee-arc` binary distribution
   ```
   $ wget https://sourceforge.net/projects/dcm4che/files/dcm4chee-arc-light5/5.10.5/dcm4chee-arc-5.10.5-mysql-secure-ui.zip
   $ unzip dcm4chee-arc-5.10.5-mysql-secure-ui.zip
   ```

2. Download the `wildfly` application server
   ```
   $ wget -qO- http://download.jboss.org/wildfly/10.1.0.Final/wildfly-10.1.0.Final.tar.gz | tar xvz
   ```

3. Download the mySQL JDBC connector
   ```
   $ wget -qO- https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.44.tar.gz | tar xvz
   ```

4. Create `dcm4chee-arc-config.json` file below to set user settings and permissions to the MySQL and OpenLDAP servers. Change the values according to your setup.

    **Don't worry about keycloak keys properties at this moment. Leave them as it is. We will update them later.**

    ```json
    {
      "dcm4cheeDir": "/home/vagrant/dcm4chee-arc-5.10.5-mysql-secure-ui",
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
      "jdbcJarFile" : "/home/vagrant/mysql-connector-java-5.1.44/mysql-connector-java-5.1.44-bin.jar",
      "keycloak": {
        "dcm4che-public-key": "<COPY_PASTE_DCM4CHE_PUBLIC_KEY_HERE>",
        "dcm4che-arc-ui-secret-key": "<COPY_PASTE_DC4CHE-ARC-UI_SECRET_KEY_HERE>",
        "dcm4che-arc-rs-secret-key": "<COPY_PASTE_DC4CHE-ARC-RS_SECRET_KEY_HERE>"
      }
    }
    ```

5. Run the installation script:
    ```bash
    $ wget https://raw.githubusercontent.com/avansp/dcm4chee-arc-notes/master/centos7-mysql-secured/install-dcm4chee-arc-mysql-secure.py
    $ python install-dcm4chee-arc-mysql-secure.py dcm4chee-arc-config.json
    ```

6. Start the `WildFly` with `dcm4chee-arc.xml` setting
   ```
   $ ~/wildfly-10.1.0.Final/bin/standalone.sh -b 0.0.0.0 -c dcm4chee-arc.xml
   ```
   Note the binding address `0.0.0.0` in order to accept webpage request from all sources.

7. Open a shell in another terminal.

   *You can open another shell by calling `vagrant ssh` again from your guest machine*


8. Install Keycloak adapter and add admin user:
   ```
   $ ~/wildfly-10.1.0.Final/bin/jboss-cli.sh -c --file=wildfly-10.1.0.Final/bin/adapter-install.cli
   $ ~/wildfly-10.1.0.Final/bin/add-user-keycloak.sh --user admin
   Password:
   ```

9. **Restart Wildfly**
   `CTRL+C` on the terminal output of Step 6, then run it again.


# Create Keycloak user roles, accounts and permissions

You need to do the following steps manually on a browser:

1. Open http://localhost:8080/auth

2. Go to Administration Console and login with `admin` user that you created on the Step 8 above.

3. Add new realm called
   ```
       Name: dcm4che
   ```

4. Using `dcm4che` realm, create a new client
   ```
      Client ID : dcm4chee-arc-ui
   ```
   After clicking `Save` button, set the following properties:
   ```
      Valid Redirect UIs : /dcm4chee-arc/ui2/*
      Admin URL : /dcm4chee-arc/ui2/
      Access Type : Confidential
   ```
   Click `Save` button.

5. Create another new client for the RESTful services:
   ```
      Client ID : dcm4chee-arc-rs
   ```
   with the following properties
   ```
      Valid Redirect UIs : /dcm4chee-arc/*
      Admin URL : /dcm4chee-arc
      Access Type : Confidential
   ```

6. Add new **Roles**:
   ```
      Role name : admin
      Role name : auditlog
      Role name : user
   ```

7. Add new **Users**:
   ```
      Username : user
      Under the Role Mappings tab, map the 'user' role to this newly created user.
      Under the Credentials tab, set the Password for this user.

      Username : admin
      Under the Role Mappings tab, map the 'user', 'auditlog' and 'admin' roles to this newly created user.
      Under the Credentials tab, set the Password for this user.
   ```

8. Go to **Events** leftside menu / **Config** tab, add `dcm4che-audit` to the **Event Listeners** field.

9. Edit the `dcm4chee-arc-config.json` file and update the keycloak's keys as follows:
   ```
      dcm4che-public-key : go to Realm Settings -> keys tab -> view public key
      dcm4che-arc-ui-secret-key : go to Clients -> dcm4che-arc-ui -> Credentials -> Secret
      dcm4che-arc-rs-secret-key : go to Clients -> dcm4che-arc-rs -> Credentials -> Secret
   ```

10. Logout from the Keycloak web.


# Deploy the `dcm4chee-arc` server

1. **Restart Wildfly**

2. Configure the wildfly using another script:
   ```
   $ wget https://raw.githubusercontent.com/avansp/dcm4chee-arc-notes/master/centos7-mysql-secured/configure-dcm4chee-arc-secure.py
   $ python configure-dcm4chee-arc-secure.py dcm4chee-arc-config.json
   ```  

4. Open the UI at http://localhost:8080/dcm4chee-arc/ui2


-----
**ENJOY!!**
