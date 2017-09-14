#!/usr/bin/python3

import json, argparse
from time import gmtime, strftime
import subprocess, re, os


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


def SetupWildFly(dcm4cheeDir, wildflyHome):
    """
    Setup the WildFly configuration
    """

    print('DCM4CHEE-ARC DIR = ' + dcm4cheeDir)
    print('WILDFLY DIR = ', wildflyHome)

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
    parser = argparse.ArgumentParser()
    parser.add_argument('configFile', help='DCM4CHEE-ARC configuration file in JSON format.')
    args = parser.parse_args()

    # reading configuration file
    with open(args.configFile) as f:
            config = json.load(f)
    f.close()

    # running some checks
    logtime("Configuring WildFly")
    SetupWildFly(config['dcm4cheeDir'], config['wildflyHome'])

    logtime("FINISHED.")
    print("Start WildFly in standalone as: " + \
          bcolors.OKBLUE + \
          config['wildflyHome'] + "/bin/standalone.sh -b 0.0.0.0 -c dcm4chee-arc.xml" + \
          bcolors.ENDC)
