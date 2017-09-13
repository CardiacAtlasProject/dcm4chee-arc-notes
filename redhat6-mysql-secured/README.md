This is a highly opinionated installation notes for **secured** dcm4chee-arc server.

Status: *in progress*

# I'm using ...

1. RedHat 6.8 server.
2. [MySQL 5.7.19](https://www.mysql.com/) community edition for the pacs database.
3. [OpenLDAP](https://www.openldap.org/) server for the ldap server.
4. [Wildfly 10.1.0](http://wildfly.org/) for the application server.
5. Python 3.4 for running installation/configuration scripts.

**Some notes on installing python 3.4 with RedHat:**
```
$ wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm
$ sudo rpm -ivh epel-release-latest-6.noarch.rpm
$ sudo yum clean all
$ sudo yum install python3 python34-setuptools python34-devel
$ sudo easy_install-3.4 pip
```
The reason why I'm using python 3 is that RedHat 6.8 installed python 2.6, but mysql-connector requires python 2.7 or above. Installing python 2.7 without breaking yum is a hassle since you must compile them.

# Install OpenLDAP server

If you have not installed an OpenLDAP server, here are the steps:
```
$ sudo yum -y install openldap compat-openldap openldap-clients openldap-servers openldap-servers-sql openldap-devel
$ sudo service slapd start
$ sudo chkconfig slapd on
$ sudo slappasswd
New password:
Re-enter new password:
SECRET_KEY
```

The root OpenLDAP password and the `SECRET_KEY` are going to be needed for later steps. So, I make references for this note as:
* **`$ROOT_OPENLDAP_PASSWD`** for the root password
* **`$SECRET_KEY_OPENLDAP`** for the SECRET_KEY generated from the last command above


# Download some binaries

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
     "dcm4cheeDir": "<PATH_TO_DCM4CHEE-ARC_FOLDER>/dcm4chee-arc-5.10.5-mysql-secure-ui",
     "wildflyHome": "<PATH_TO_WILDFLY_FOLDER>/wildfly-10.1.0.Final",
     "mysql": {
       "host": "localhost",
       "port": 3306,
       "rootPasswd": "<ROOT_PASSWORD_TO>",
       "dbName": "<DATABASE_NAME_YOU_WANT_TO_CREATE_FOR_DCM4CHEE-ARC>",
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


# Configure the MySQL server

Assume you have installed MySQL server and have root access.

Make sure you have installed `pip`, and mysql connector for python3. Note that I'm using [mysqlclient](https://github.com/PyMySQL/mysqlclient-python) module to connect to MySQL server using python3, because MySQL does not provide connector for python3.

Here's how I installed the `mysqlclient` module;
```
$ sudo yum install mysql-devel
$ sudo pip install mysqlclient
```
See the mysqlclient documentation from https://mysqlclient.readthedocs.io/index.html

Configure the MySQL server:
```
$ wget https://raw.githubusercontent.com/avansp/dcm4chee-arc-notes/master/redhat6-mysql-secured/configure-mysql.py
$ python3 configure-mysql.py dcm4chee-arc-config.json
```

# Configure WildFly

Full details are given in https://github.com/dcm4che/dcm4chee-arc-light/wiki/Installation-and-Configuration

1. Run the installation script:
    ```bash
    $ wget https://raw.githubusercontent.com/avansp/dcm4chee-arc-notes/master/redhat6-mysql-secured/configure-openldap.py
    $ python3 configure-openldap.py dcm4chee-arc-config.json
    ```

2. Start the `WildFly` with `dcm4chee-arc.xml` setting
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
