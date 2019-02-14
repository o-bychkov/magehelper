#!/usr/bin/python3
import re
import os
import argparse
from datetime import datetime


def get_database_credentials():
    with open(r'./app/etc/env.php') as file:
        config_file = ' '.join(file.read().split())

    regex = re.findall(r"'db'(.*?)(\),|],)", config_file, flags=re.DOTALL)
    for elem in regex:
        elem = ''.join(elem)
        if 'host' in elem and 'dbname' in elem and 'username' in elem:
            credentials_block = elem

    database_credentials = dict()
    database_credentials['host'] = re.search(r"'host'....'(.*?)'", credentials_block).group(1).split(':')
    database_credentials['dbname'] = re.search(r"'dbname'....'(.*?)'", credentials_block).group(1)
    database_credentials['username'] = re.search(r"'username'....'(.*?)'", credentials_block).group(1)
    database_credentials['password'] = re.search(r"'password'....'(.*?)'", credentials_block).group(1)
    database_credentials['table_prefix'] = re.search(r"'table_prefix'....'(.*?)'", credentials_block).group(1)

    return database_credentials


def conn_mysql():
    database_credentials = get_database_credentials()

    if len(database_credentials['host']) == 1:
        mysql_connect = "mysql -u '{}' -p'{}' '{}' -h '{}'".format(database_credentials['username'],
                                                           database_credentials['password'],
                                                           database_credentials['dbname'],
                                                           database_credentials['host'][0])

    elif len(database_credentials['host']) == 2:
        mysql_connect = "mysql -u '{}' -p'{}' '{}' -h '{}' -P '{}'".format(database_credentials['username'],
                                                                 database_credentials['password'],
                                                                 database_credentials['dbname'],
                                                                 database_credentials['host'][0],
                                                                 database_credentials['host'][1])
    
    return mysql_connect


def change_domain():
    mysql_connect = conn_mysql()
    database_credentials = get_database_credentials()

    check_domain_query = 'select * from {}core_config_data where path like "%base%url%"'.format(database_credentials['table_prefix'])
    os.system("{} -e '{}' 2>>/dev/null".format(mysql_connect, check_domain_query))

    old_domain = input('old domain: ')
    new_domain = input('new domain: ')

    replace_domain_query = "update {0}core_config_data set value = REPLACE(value, '{1}', '{2}')".format(database_credentials['table_prefix'],
                                                                                                        old_domain,
                                                                                                        new_domain)

    os.system("{0} -e \"{1}\" 2>>/dev/null".format(mysql_connect, replace_domain_query))
    os.system("{0} -e '{1}' 2>>/dev/null".format(mysql_connect, replace_domain_query))


def create_database_backup():
    mysql_connect = conn_mysql()
    mysql_connect = mysql_connect.replace('mysql', 'mysqldump', 1)

    time_now = datetime.now().strftime("%m%d%y%H%M%S")

    os.system("{0} --single-transaction | sed -e 's/DEFINER[ ]*=[ ]*[^*]*\*/\*/' | gzip > ./var/{1}db_dump.sql.gz".format(mysql_connect, time_now))
    file_size = os.stat('./var/{0}db_dump.sql.gz'.format(time_now))

    return "./var/{0}db_dump.sql.gz {1}".format(time_now, file_size.st_size)


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('change', help='Change domain in database.')
    subparsers.add_parser('backup', help='Create database backup')
    subparsers.add_parser('get', help='Get string for connect')
    subparsers.add_parser('dbname', help='Get dbname')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    if args.command == 'change':
        change_domain()

    elif args.command == 'backup':
        print(create_database_backup())

    elif args.command == 'get':
        print(conn_mysql())

    elif args.command == 'dbname':
        print(get_database_credentials()['dbname'])
