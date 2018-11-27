#!/usr/bin/python3
import re
from ast import literal_eval
import os


with open(r'./app/etc/env.php') as file:
    config_file = ' '.join(file.read().split())
with open(r'./app/etc/env.php') as file:
    config_file_origin = ' '.join(file.read().split())

config_file = re.sub(r'\(', '[', config_file)
config_file = re.sub(r'\)', ']', config_file)

start = [elem for elem in reversed(range(config_file.find('dbname'))) if config_file[elem] == '[']
end = [elem for elem in range(config_file.find('dbname'), len(config_file)) if config_file[elem] == ']']

config_file = config_file[start[0]:end[0]+1]

password = re.search("'password' => '(.*?)'", config_file_origin)

config_file = re.sub(r' =>', ':', config_file)
config_file = re.sub(r'\[', '{', config_file)
config_file = re.sub(r'\]', '}', config_file)
config_file = literal_eval(config_file)

host = config_file['host'].split(':')

if len(host) == 1:
    mysql_connect = "mysql -u {} -p{} {} -h {}".format(config_file['username'],
                                                       password.group(1),
                                                       config_file['dbname'],
                                                       host[0])

elif len(host) == 2:
    print(host[1])
    mysql_connect = "mysql -u {} -p{} {} -h {} -P {}".format(config_file['username'],
                                                             password.group(1),
                                                             config_file['dbname'], host[0], host[1])

else:
    print('Error!')
    exit()

query_check_domain = 'select * from core_config_data where path like "%base%url%"'
os.system("{} -e '{}' 2>>/dev/null".format(mysql_connect, query_check_domain))

old_domain = input('old domain: ')
new_domain = input('new domain: ')

query_replace_domain = "update core_config_data set value = REPLACE(value, '{}', '{}')".format(old_domain, new_domain)

os.system("{} -e \"{}\" 2>>/dev/null".format(mysql_connect, query_replace_domain))
print('Done!')
os.system("{} -e '{}' 2>>/dev/null".format(mysql_connect, query_check_domain))

exit()
