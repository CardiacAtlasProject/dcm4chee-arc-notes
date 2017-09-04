#!/usr/bin/python
"""Install dcm4chee-arc-light secured ui version

Usage:
    install-dcm4chee-arc-mysql-secure.py <configFile>
    install-dcm4chee-arc-mysql-secure.py -h

Argument:
    configFile    A JSON configuration file.

Options:
    -h, --help              Show this screen

Author: Avan Suinesiaputra - @asui085
"""

from time import gmtime, strftime
import docopt, subprocess, shlex, json, os, sys, re, shutil
import mysql.connector as mysql
from lxml import etree as ET

mainConfig = []

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def logtime(_msg):
    """
    Just print a formatted datetime now.
    """
    print(bcolors.HEADER + "[" + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "]: " + _msg + bcolors.ENDC)

def ok():
    print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)

def fail(_msg):
    print(bcolors.FAIL + "FAILED: " + _msg + bcolors.ENDC)
    sys.exit()

def SetupMySQL():
    """
    Configure and setup MySQL
    """

    logtime("Setting up PACS database on MySQL server")

    # connecting
    mysqlConfig = mainConfig['mysql']
    print 'Connecting to mysql://' + mysqlConfig['host'] + ':' + str(mysqlConfig['port']) + ' ...'

    try:
        cnx = mysql.connect(user='root',
                            host=mysqlConfig['host'],
                            port=mysqlConfig['port'],
                            password=mysqlConfig['rootPasswd'])

    except mysql.Error as err:
        print(bcolors.FAIL + err + bcolors.ENDC)
        sys.exit()

    cursor = cnx.cursor(buffered=True, named_tuple=True)

    qstr = "DROP DATABASE IF EXISTS " + mysqlConfig['dbName']
    print(qstr)
    cursor.execute(qstr)

    qstr = "CREATE DATABASE " + mysqlConfig['dbName']
    print(qstr)
    cursor.execute(qstr)

    qstr = "CREATE USER IF NOT EXISTS'" + mysqlConfig['userName'] + "'@'%' IDENTIFIED BY '" + mysqlConfig['userPasswd'] + "' PASSWORD EXPIRE NEVER"
    print(qstr)
    cursor.execute(qstr)

    qstr = "GRANT ALL ON " + mysqlConfig['dbName'] + ".* TO '" + mysqlConfig['userName'] + "'@'%' IDENTIFIED BY '" + mysqlConfig['userPasswd'] + "'"
    print(qstr)
    cursor.execute(qstr)

    print("Creating tables in " + mysqlConfig['dbName'])
    cursor.execute("USE " + mysqlConfig['dbName'])
    with open(mainConfig['dcm4cheeDir'] + r'/sql/create-mysql.sql') as f:
        for line in f:
            cursor.execute(line)
    f.close()

    cnx.close()


def SetupOpenLDAP():
    """
    Configure the OpenLDAP server for dcm4chee-arc
    """

    logtime("Setting up PACS database on OpenLDAP server")

    ldapConfig = mainConfig['ldap']

    olcSuffix = "dc=" + re.sub('\.',',dc=',ldapConfig['domainName'])
    print("Domain context name = " + olcSuffix)

    # create a temporary modify-baseDN.ldif
    with open('/tmp/modify-baseDN.ldif', 'w') as f:
        f.write('dn: olcDatabase={2}hdb,cn=config\n')
        f.write('changetype: modify\n')
        f.write('replace: olcSuffix\n')
        f.write('olcSuffix: ' + olcSuffix + '\n')
        f.write('\n')
        f.write('dn: olcDatabase={2}hdb,cn=config\n')
        f.write('changetype: modify\n')
        f.write('replace: olcRootDN\n')
        f.write('olcRootDN: cn=admin,' + olcSuffix + '\n')
        f.write('\n')
        f.write('dn: olcDatabase={2}hdb,cn=config\n')
        f.write('changetype: modify\n')
        f.write('replace: olcRootPW\n')
        f.write('olcRootPW: ' + ldapConfig['olcRootPW'] + '\n')

    f.close()

    print("Modify root DN")
    subprocess.call(["sudo", "ldapmodify", "-Y", "EXTERNAL", "-H", "ldapi:///", "-f", "/tmp/modify-baseDN.ldif"])

    print("sudo ldapadd -Y EXTERNAL -H ldapi:/// -f $DCM4CHEE_ARC/ldap/slapd/dicom.ldif")
    subprocess.call(["sudo", "ldapadd", "-Y", "EXTERNAL", "-H", "ldapi:///", "-f", \
                     mainConfig['dcm4cheeDir'] + "/ldap/slapd/dicom.ldif" ])

    print("sudo ldapadd -Y EXTERNAL -H ldapi:/// -f $DCM4CHEE_ARC/ldap/slapd/dcm4che.ldif")
    subprocess.call(["sudo", "ldapadd", "-Y", "EXTERNAL", "-H", "ldapi:///", "-f", \
                     mainConfig['dcm4cheeDir'] + "/ldap/slapd/dcm4che.ldif" ])

    print("sudo ldapadd -Y EXTERNAL -H ldapi:/// -f $DCM4CHEE_ARC/ldap/slapd/dcm4chee-archive.ldif")
    subprocess.call(["sudo", "ldapadd", "-Y", "EXTERNAL", "-H", "ldapi:///", "-f", \
                     mainConfig['dcm4cheeDir'] + "/ldap/slapd/dcm4chee-archive.ldif" ])

    # create a temporary init-baseDN.ldif
    with open('/tmp/init-baseDN.ldif', 'w') as f:
        f.write('version: 1\n\n')
        f.write('dn: ' + olcSuffix + '\n')
        f.write('objectClass: top\n')
        f.write('objectClass: dcObject\n')
        f.write('objectClass: organization\n')
        f.write('o: ' + ldapConfig['domainName'] + '\n')
        f.write('dc: ' + re.sub('\..*$','',ldapConfig['domainName']) + '\n')
    f.close()

    subprocess.call(['sudo', 'ldapadd', '-x', '-w', ldapConfig['rootPasswd'], '-D', 'cn=admin,' + olcSuffix, \
                     '-f', '/tmp/init-baseDN.ldif'])

    # load ldif files
    sedStr = 's/dc=dcm4che,dc=org/' + olcSuffix + '/'

    f = open('/tmp/init-config.ldif','w')
    subprocess.call(['sed', sedStr, mainConfig['dcm4cheeDir'] + '/ldap/init-config.ldif'], stdout=f)
    f.close()
    subprocess.call(['sudo', 'ldapadd', '-x', '-w', ldapConfig['rootPasswd'], '-D', 'cn=admin,' + olcSuffix, \
                     '-f', '/tmp/init-config.ldif'])

    f = open('/tmp/default-config.ldif','w')
    subprocess.call(['sed', sedStr, mainConfig['dcm4cheeDir'] + '/ldap/default-config.ldif'], stdout=f)
    f.close()
    subprocess.call(['sudo', 'ldapadd', '-x', '-w', ldapConfig['rootPasswd'], '-D', 'cn=admin,' + olcSuffix, \
                     '-f', '/tmp/default-config.ldif'])

    f = open('/tmp/add-vendor-data.ldif','w')
    subprocess.call(['sed', sedStr, mainConfig['dcm4cheeDir'] + '/ldap/add-vendor-data.ldif'], stdout=f)
    f.close()
    subprocess.call(['sed', '-i', 's/vendor-data.zip/' + re.sub('/','\\/',mainConfig['dcm4cheeDir']) + r'\/ldap\/vendor-data.zip/', '/tmp/add-vendor-data.ldif'])
    subprocess.call(['sudo', 'ldapmodify', '-x', '-w', ldapConfig['rootPasswd'], '-D',  \
                     'cn=admin,' + olcSuffix, '-H', 'ldap:///', '-f', '/tmp/add-vendor-data.ldif'])


def SetupWildFly():
    """
    Configure and setup the application server WildFly
    """

    logtime("Setting up WildFly")

    dcm4cheeDir = mainConfig['dcm4cheeDir']
    wildflyHome = mainConfig['wildflyHome']

    print('cp -r $DCM4CHEE_ARC/configuration/dcm4chee-arc $WILDFLY_HOME/standalone/configuration')
    subprocess.call(['cp', '-r', dcm4cheeDir + '/configuration/dcm4chee-arc', wildflyHome + '/standalone/configuration'])

    # replace ldap.properties
    olcSuffix = "dc=" + re.sub('\.',',dc=',mainConfig['ldap']['domainName'])
    propfile = wildflyHome + '/standalone/configuration/dcm4chee-arc/ldap.properties'
    subprocess.call(['sed', '-i', 's/dc=dcm4che,dc=org/' + olcSuffix + '/', propfile])
    subprocess.call(['sed', '-i', 's/secret/' + mainConfig['ldap']['rootPasswd'] + '/', propfile])

    # copy files
    print('Copy standalone-full.xml to dcm4chee-arc.xml')
    shutil.copyfile(wildflyHome + '/standalone/configuration/standalone-full.xml', wildflyHome + '/standalone/configuration/dcm4chee-arc.xml')

    # -- SECURE VERSIOON
    print('Download keycloak access management')
    ps = subprocess.Popen(['wget', '-qO-', 'https://downloads.jboss.org/keycloak/2.4.0.Final/keycloak-overlay-2.4.0.Final.tar.gz'], stdout=subprocess.PIPE)
    subprocess.call(['tar', 'xvz', '-C', wildflyHome], stdin=ps.stdout)

    ps = subprocess.Popen(['wget', '-qO-', 'https://downloads.jboss.org/keycloak/2.4.0.Final/adapters/keycloak-oidc/keycloak-wildfly-adapter-dist-2.4.0.Final.tar.gz'], stdout=subprocess.PIPE)
    subprocess.call(['tar', 'xvz', '-C', wildflyHome], stdin=ps.stdout)

    print('Modify keycloak-install.cli')
    subprocess.call(['sed', '-i', 's/standalone.xml/dcm4chee-arc.xml/', wildflyHome + '/bin/keycloak-install.cli'])
    subprocess.call(['sed', '-i', 's/default-keycloak-subsys-config.cli/' + \
       re.sub('/','\\/', wildflyHome + '/bin/') + 'default-keycloak-subsys-config.cli/', \
       wildflyHome + '/bin/keycloak-install.cli'])
    subprocess.call([wildflyHome + '/bin/jboss-cli.sh', '--file=' + wildflyHome + '/bin/keycloak-install.cli'])

    # ---- MODIFYING dcm4chee-arc.xml
    tree = ET.parse(wildflyHome + '/standalone/configuration/dcm4chee-arc.xml')

    ks = tree.find('.//{urn:jboss:domain:keycloak-server:1.1}subsystem')

    provks = ks.find('.//{urn:jboss:domain:keycloak-server:1.1}providers')
    newProvider = ET.SubElement(provks, 'provider')
    newProvider.text = 'module:org.dcm4che.audit-keycloak'

    nSpi = ET.SubElement( ks, 'spi', name="eventsListener" )
    nProvider = ET.SubElement( nSpi, 'provider', name="dcm4che-audit", enabled="true")
    nProps = ET.SubElement( nProvider, 'properties' )
    ET.SubElement( nProps, 'property', name="includes", \
                   value='["LOGIN", "LOGIN_ERROR", "LOGOUT", "LOGOUT_ERROR"]')

    newSysProp = ET.Element( 'system-properties' )
    ET.SubElement( newSysProp, 'property', name="auth-server-url", value="/auth" )
    ET.SubElement( newSysProp, 'property', name="realm-name", value="dcm4che" )
    tree.getroot().insert(1, newSysProp )

    sdpe = tree.find('.//{urn:jboss:domain:ee:4.0}subsystem').find('.//{urn:jboss:domain:ee:4.0}spec-descriptor-property-replacement')
    sdpe.text = 'true'

    # overwrite to dcm4chee-arc.xml file
    with open(wildflyHome + '/standalone/configuration/dcm4chee-arc.xml', 'w') as f:
        f.write(ET.tostring(tree, encoding="UTF-8", xml_declaration=True, pretty_print=True))
    f.close()
    # ---- END-OF-MODIFICATION

    # -- END-OF-SECURE VERSION

    print('Copy dcm4chee-arc-light libraries as JBoss modules')
    subprocess.call(['unzip', '-o', dcm4cheeDir + '/jboss-modules/dcm4che-jboss-modules-5.10.5.zip', '-d', wildflyHome])

    print('Copy JAI ImageIO 1.2 libraries as JBoss modules')
    subprocess.call(['unzip', '-o', dcm4cheeDir + '/jboss-modules/jai_imageio-jboss-modules-1.2-pre-dr-b04.zip', '-d', wildflyHome])

    print('Copy QueryDSL 4.1.4 libraries as JBoss modules')
    subprocess.call(['unzip', '-o', dcm4cheeDir + '/jboss-modules/querydsl-jboss-modules-4.1.4-noguava.zip', '-d', wildflyHome])

    print('Copy jclouds 1.9.2 libraries as JBoss modules')
    subprocess.call(['unzip', '-o', dcm4cheeDir + '/jboss-modules/jclouds-jboss-modules-1.9.2-noguava.zip', '-d', wildflyHome])

    print('Copy ecs-object-client 3.0.0 libraries as JBoss modules')
    subprocess.call(['unzip', '-o', dcm4cheeDir + '/jboss-modules/ecs-object-client-jboss-modules-3.0.0.zip', '-d', wildflyHome])

    print('Copy MySQL JDBC connector')
    print('JDBC jar file = ' + mainConfig['jdbcJarFile'])
    subprocess.call(['unzip', '-o', dcm4cheeDir + '/jboss-modules/jdbc-jboss-modules-1.0.0-mysql.zip', '-d', wildflyHome])
    subprocess.call(['cp', mainConfig['jdbcJarFile'], wildflyHome + '/modules/com/mysql/main/'])
    subprocess.call(['sed', '-i', 's/mysql.*jar/' + os.path.basename(mainConfig['jdbcJarFile']) + '/', wildflyHome + '/modules/com/mysql/main/module.xml'])


if __name__ == "__main__":
    try:
        # Parse arguments, use file docstring as a parameter definition
        arguments = docopt.docopt(__doc__)

    # Handle invalid options
    except docopt.DocoptExit as e:
        print e.message
        exit()

    # read configuration file
    with open(arguments['<configFile>']) as f:
        mainConfig = json.load(f)
    f.close()

    logtime("Start installation")
    print("DCM4CHEE_DIR = " + mainConfig['dcm4cheeDir'])
    print("WILDFLY_HOME = " + mainConfig['wildflyHome'])

    SetupMySQL()
    SetupOpenLDAP()
    SetupWildFly()

    # cleaning up
    for f in ['modify-baseDN.ldif', 'init-baseDN.ldif', 'init-config.ldif', 'default-config.ldif', 'add-vendor-data.ldif']:
        os.remove('/tmp/' + f)

    logtime("FINISHED.")
    print("Start WildFly in standalone as: " + \
          bcolors.OKBLUE + \
          mainConfig['wildflyHome'] + "/bin/standalone.sh -b 0.0.0.0 -c dcm4chee-arc.xml" + \
          bcolors.ENDC)
