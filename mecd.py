#!/usr/bin/python3
import re
from ast import literal_eval
import os


with open(r'app/etc/env.php') as config_file:
    config_file = ' '.join(config_file.read().split())

config_file = re.search(r"'connection' => ((.|\n)*?)\],", config_file).group(1)
config_file = re.sub(r' =>', ':', config_file)
config_file = re.sub(r'\[', '{', config_file)
config_file = re.sub(r'\]', '}', config_file)
config_file = literal_eval(config_file)

host = config_file['default']['host'].split(':')

if len(host) == 1:
    mysql_connect = "mysql -u {} -p{} {} -h {}".format(config_file['default']['username'],
                                                       config_file['default']['password'],
                                                       config_file['default']['dbname'],
                                                       host[0])

elif len(host) == 2:
    print(host[1])
    mysql_connect = "mysql -u {} -p{} {} -h {} -P {}".format(config_file['default']['username'],
                                                             config_file['default']['password'],
                                                             config_file['default']['dbname'], host[0], host[1])

else:
    print('Error!')
    exit()

# Old idea
# def regex(value):
#     config_file = open(r'/home/olezzha/thrash/env.php')
#     result = re.findall("'db'(.+?)\],".format(value, ), str(config_file.readlines()))
#     config_file.close()
#     return (re.search(r"'{}' => (.+?),".format(value, ), *result).group(1))[1:-1]

query_check_domain = 'select * from core_config_data where path like "%base%url%"'
os.system("{} -e '{}' 2>>/dev/null".format(mysql_connect, query_check_domain))

old_domain = input('old domain: ')
new_domain = input('new domain: ')

query_replace_domain = "update core_config_data set value = REPLACE(value, '{}', '{}')".format(old_domain, new_domain)

os.system("{} -e \"{}\" 2>>/dev/null".format(mysql_connect, query_replace_domain))
print('Done!')
os.system("{} -e '{}' 2>>/dev/null".format(mysql_connect, query_check_domain))

exit()
