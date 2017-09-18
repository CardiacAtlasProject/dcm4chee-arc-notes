# Application Entity (AE) Titles

There are three default AE Titles: `DCM4CHEE`, `DCM4CHEE-ADMIN` and `DCM4CHEE-THRASH`. You should rename these AE titles for your unique PACS connection.

Follow this guideline to change AETitle(s) of the archive: https://github.com/dcm4che/dcm4chee-arc-light/wiki/AE-Title(s)-of-the-Archive

# The port numbers

Open `$WILDFLY_HOME/standalone/configuration/dcm4chee-arc.xml` and adjust port numbers in:
```xml
  <socket-binding-group name="standard-sockets" default-interface="public" port-offset="${jboss.socket.binding.port-offset:0}">
    <socket-binding name="management-http" interface="management" port="${jboss.management.http.port:9990}"/>
    <socket-binding name="management-https" interface="management" port="${jboss.management.https.port:9993}"/>
    <socket-binding name="ajp" port="${jboss.ajp.port:8009}"/>
    <socket-binding name="http" port="${jboss.http.port:8080}"/>
    <socket-binding name="https" port="${jboss.https.port:8443}"/>
    <socket-binding name="iiop" interface="unsecure" port="3528"/>
    <socket-binding name="iiop-ssl" interface="unsecure" port="3529"/>
    <socket-binding name="txn-recovery-environment" port="4712"/>
    <socket-binding name="txn-status-manager" port="4713"/>
    <outbound-socket-binding name="mail-smtp">
        <remote-destination host="localhost" port="25"/>
    </outbound-socket-binding>
  </socket-binding-group>
```

# DICOM object storage location

The default storage location for DICOM objects is at `$WILDFLY_HOME/standalone/data/fs1/`, which is not what you want. This setting is written in the LDAP dictionary. You can either use `ldapmodify` CLI function to modify the LDAP entry or [Apache Directory Studio](https://directory.apache.org/studio/) to modify the entry using a user interface. See [this guideline](https://github.com/dcm4che/dcm4chee-arc-light/wiki/Generic-Storage) on how to change the storage location for dcm4chee.

Example, a simple configuration where all DICOM objects are stored in one location, say `/opt/ARCHIVE` and assume that your domain context name is `dc=dcm4chee,dc=org`. Write the a file `storage.ldif` file that contains:
```
version: 1
dn: dcmStorageID=fs1,dicomDeviceName=dcm4chee-arc,cn=Devices,cn=DICOM Configuration,dc=dcm4chee,dc=org
changetype: modify
replace: dcmURI
dcmURI: file:/opt/ARCHIVE/
```

Then on command line:
```
$ sudo ldapmodify -x -D "cn=admin,dc=dcm4chee,dc=org" -H ldap:/// -W -f storage.ldif
Enter LDAP password:
```

You can check it by using the following command:
```
$ sudo ldapsearch -x -W -D "cn=admin,dc=dcm4chee,dc=org" -H ldap:/// -b "dcmStorageID=fs1,dicomDeviceName=dcm4chee-arc,cn=Devices,cn=DICOM Configuration,dc=dcm4chee,dc=org"
```

**Restart dcm4chee-arc server to load the new configuration**

# Test DICOM connection

You can send DICOM C-ECHO message using [dcm4che tool's storescu](https://github.com/dcm4che/dcm4che) command line. Assume that your `AET=DCM4CHEE` and your host is `localhost`, then
```
$ storescu -c DCM4CHEE@localhost:11112
```

# Upload a study

1. Using [dcm4che tool](https://github.com/dcm4che/dcm4che) :
   ```
   $ storescu -c DCM4CHEE@localhost:11112 <STUDY_DIRECTORY>
   ```
