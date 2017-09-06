#!/usr/bin/python
"""Configure dcm4chee-arc. You must run the dcm4chee-arc server.

Usage:
    configure-dcm4chee-arc.py <configFile>
    configure-dcm4chee-arc.py -h

Argument:
    configFile    A JSON configuration file.

Options:
    -h, --help              Show this screen

Author: Avan Suinesiaputra - @asui085
"""

from time import gmtime, strftime
import docopt, subprocess, shlex, json, os, sys, re, shutil
import mysql.connector as mysql

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

    logtime("Configure dcm4chee-arc")
    print("DCM4CHEE_DIR = " + mainConfig['dcm4cheeDir'])
    print("WILDFLY_HOME = " + mainConfig['wildflyHome'])

    jbossCLI = mainConfig['wildflyHome'] + r'/bin/jboss-cli.sh'

    print('Add data source')
    with open('/tmp/add-data-source.cli','w') as f:
        f.write('/subsystem=datasources/jdbc-driver=mysql:add(driver-name=mysql,driver-module-name=com.mysql)\n')
        f.write('data-source add --name=PacsDS --driver-name=mysql --jndi-name=java:/PacsDS \\\n')
        f.write('--connection-url=jdbc:mysql://' + mainConfig['mysql']['host'] + ':3306/' + mainConfig['mysql']['dbName'] + ' \\\n')
        f.write('--user-name=' + mainConfig['mysql']['userName'] + ' --password=' + mainConfig['mysql']['userPasswd'] + '\n' )
        f.write('data-source enable --name=PacsDS')
    f.close()
    subprocess.call([jbossCLI, '-c', '--file=/tmp/add-data-source.cli'])

    print('Add JMS Queues')
    subprocess.call([jbossCLI, '-c', '--file=' + mainConfig['dcm4cheeDir'] + '/cli/add-jms-queues.cli'])

    print('Deploying')
    with open('/tmp/deploy.cli','w') as f:
        f.write('/subsystem=ee/managed-executor-service=default:undefine-attribute(name=hung-task-threshold)\n')
        f.write('/subsystem=ee/managed-executor-service=default:write-attribute(name=long-running-tasks,value=true)\n')
        f.write('/subsystem=ee/managed-executor-service=default:write-attribute(name=core-threads,value=2)\n')
        f.write('/subsystem=ee/managed-executor-service=default:write-attribute(name=max-threads,value=100)\n')
        f.write('/subsystem=ee/managed-executor-service=default:write-attribute(name=queue-length,value=0)\n')
        f.write('deploy ' + mainConfig['dcm4cheeDir'] + '/deploy/dcm4chee-arc-ear-5.10.5-mysql.ear \n')
    f.close()
    subprocess.call([jbossCLI, '-c', '--file=/tmp/deploy.cli'])

    # cleaning up
    for f in ['add-data-source.cli', 'deploy.cli']:
        os.remove('/tmp/' + f)

    logtime("FINISHED.")
    print("The DCM4CHEE-ARC webpage can be access from: " + \
          bcolors.OKBLUE + \
          'http://localhost:8080/dcm4chee-arc/ui2' + \
          bcolors.ENDC)
