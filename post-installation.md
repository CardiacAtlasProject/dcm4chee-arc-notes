# Application Entity (AE) Title

There are three default AE Titles: `DCM4CHEE`, `DCM4CHEE-ADMIN` and `DCM4CHEE-THRASH`. You should rename these AE titles for your unique PACS connection.

Follow this guideline to change AETitle(s) of the archive: https://github.com/dcm4che/dcm4chee-arc-light/wiki/AE-Title(s)-of-the-Archive

# Changing the port numbers

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

# The image storage location

The default storage location for images is at `$WILDFLY_HOME/standalone/data/fs1/`, which is not what you want. This setting is written in the LDAP dictionary. You either use `ldapmodify` CLI function to modify the LDAP entry, or use [Apache Directory Studio](https://directory.apache.org/studio/) to modify the entry using user interface. See t[this guideline](https://github.com/dcm4che/dcm4chee-arc-light/wiki/Generic-Storage) on how to change the storage location for dcm4chee.
