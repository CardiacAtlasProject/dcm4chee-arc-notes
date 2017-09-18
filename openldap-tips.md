DCM4CHEE-ARC heavily uses LDAP directory structure to store parameters. Some of these can be adjusted from the UI, e.g. AE titles, but lots of them are not. The easiest way to manipulate them is by using the [Apache Directory Studio](http://directory.apache.org/studio/), where you connect to the LDAP server directly, but you must open port 389 (if you're not in the server). The safest way is to run LDAP CLI's directly.

### Dumping the LDAP database

Use `slapcat`
```
$ sudo slapcat
```

### Backup and restore

Backup DICOM configuration into `dicom.ldif` file:
```
$ sudo slapcat -n 2 -l dicom.ldif
```

Restore
```
$ sudo mv /var/lib/ldap /var/lib/ldap`date '+%Y-%m-%d'`
$ sudo slapadd -n 1 -F /etc/openldap/slapd.d -l dicom.ldif
$ sudo chown -R ldap:ldap /var/lib/ldap
```

### Search an entry

Assume that your base domain context is `dc=my-domain,dc=com`

* Search one subtree under DICOM configuration database:
  ```
  $ ldapsearch -D "cn=admin,dc=my-domain,dc=com" -H ldap:/// -x -W -b "cn=DICOM Configuration,dc=my-domain,dc=com" -s one
  Enter LDAP Password;
  ```
