#!/usr/bin/python3
import re
import os

with open(r'./app/etc/env.php') as file:
    config_file = ' '.join(file.read().split())

regex = re.findall(r'\((.*?)\),\s', config_file, flags=re.DOTALL)
for elem in regex:
    if 'host' in elem and 'dbname' in elem and 'username' in elem:
        database_credentials = elem

host = re.search(r"'host'....'(.*?)'", database_credentials).group(1).split(':')
dbname = re.search(r"'dbname'....'(.*?)'", database_credentials).group(1)
username = re.search(r"'username'....'(.*?)'", database_credentials).group(1)
password = re.search(r"'password'....'(.*?)'", database_credentials).group(1)
table_prefix = re.search(r"'table_prefix'....'(.*?)'", database_credentials).group(1)

if len(host) == 1:
    mysql_connect = "mysql -u {} -p{} {} -h {}".format(username,
                                                       password,
                                                       dbname,
                                                       host[0])

elif len(host) == 2:
    mysql_connect = "mysql -u {} -p{} {} -h {} -P {}".format(username,
                                                             password,
                                                             dbname,
                                                             host[0],
                                                             host[1])

if table_prefix:
    query_check_domain = 'select * from {}core_config_data where path like "%base%url%"'.format(table_prefix)
else:
    query_check_domain = 'select * from core_config_data where path like "%base%url%"'

os.system("{} -e '{}' 2>>/dev/null".format(mysql_connect, query_check_domain))

old_domain = input('old domain: ')
new_domain = input('new domain: ')
if table_prefix:
    query_replace_domain = "update {0}core_config_data set value = REPLACE(value, '{1}', '{2}')".format(table_prefix,
                                                                                                        old_domain,
                                                                                                        new_domain)
else:
    query_replace_domain = "update core_config_data set value = REPLACE(value, '{0}', '{1}')".format(old_domain,
                                                                                                     new_domain)

os.system("{0} -e \"{1}\" 2>>/dev/null".format(mysql_connect, query_replace_domain))
print('Done!')
os.system("{0} -e '{1}' 2>>/dev/null".format(mysql_connect, query_check_domain))
