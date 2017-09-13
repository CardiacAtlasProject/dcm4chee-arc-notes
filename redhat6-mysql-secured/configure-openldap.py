#!/usr/bin/python3

import json, argparse
from time import gmtime, strftime
import subprocess, re


# global function
ldapConfig = []


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


def SetupOpenLDAP():
    """
    Setup open LDAP server
    """

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


    logtime("Cleaning up temporary files")

    for f in ['modify-baseDN.ldif', 'init-baseDN.ldif', 'init-config.ldif', 'default-config.ldif', 'add-vendor-data.ldif']:
        os.remove('/tmp/' + f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('configFile', help='DCM4CHEE-ARC configuration file in JSON format.')
    args = parser.parse_args()

    # reading configuration file
    with open(args.configFile) as f:
            config = json.load(f)
    f.close()

    ldapConfig = config['ldap']


    # running some checks
    logtime("Configuring OpenLDAP")
    SetupOpenLDAP()

    logtime("FINISHED.")
    print("Start WildFly in standalone as: " + \
          bcolors.OKBLUE + \
          config['wildflyHome'] + "/bin/standalone.sh -b 0.0.0.0 -c dcm4chee-arc.xml" + \
          bcolors.ENDC)
