#!/usr/bin/python3

import MySQLdb as mysql
import json, argparse
from time import gmtime, strftime


# global function
mysqlConfig = []


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


def SetupMySQL(_cursor, _dcm4cheeDir):
    """
    This function does:
    1. Drop database dbName if exist.
    2. Create database dbName.
    3. Create (if does not exist) user userName with full access to the dbName.
    4. Create dcm4chee-arc PACS tables.
    """

    userSpec = "'" + mysqlConfig['userName'] + "'@'%'"
    userPasswd = "'" + mysqlConfig['userPasswd'] + "'"

    qstr = "DROP DATABASE IF EXISTS " + mysqlConfig['dbName']
    print(qstr)
    _cursor.execute(qstr)

    qstr = "CREATE DATABASE " + mysqlConfig['dbName']
    print(qstr)
    _cursor.execute(qstr)

    qstr = "SELECT * FROM mysql.user WHERE USER='" + mysqlConfig['userName'] + "' AND HOST='%'"
    nRows = _cursor.execute(qstr)

    if nRows == 0:
        qstr = "CREATE USER IF NOT EXISTS " + userSpec + " IDENTIFIED BY " + userPasswd + " PASSWORD EXPIRE NEVER"
        print(qstr)
        _cursor.execute(qstr)

    qstr = "GRANT ALL ON " + mysqlConfig['dbName'] + ".* TO " + userSpec + " IDENTIFIED BY " + userPasswd
    print(qstr)
    _cursor.execute(qstr)

    print("Creating tables in " + mysqlConfig['dbName'])
    _cursor.execute("USE " + mysqlConfig['dbName'])
    with open(_dcm4cheeDir + r'/sql/create-mysql.sql') as f:
            for line in f:
                    _cursor.execute(line)
    f.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('configFile', help='DCM4CHEE-ARC configuration file in JSON format.')
    args = parser.parse_args()

    # reading configuration file
    with open(args.configFile) as f:
            config = json.load(f)
    f.close()
    mysqlConfig = config['mysql']


    # running some checks
    logtime("Configuring MySQL")

    print('Connecting to mysql://' + mysqlConfig['host'] + ':' + str(mysqlConfig['port']) + ' ...');

    cnx = mysql.connect(user='root',passwd=mysqlConfig['rootPasswd'],host=mysqlConfig['host'],port=mysqlConfig['port'])
    SetupMySQL(cnx.cursor(), config['dcm4cheeDir'])
    cnx.close()
