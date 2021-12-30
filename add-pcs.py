import os
import json
import requests
import subprocess

#Certain information has been withheld from the script for the sake of privacy.
#However, this should give the reader an idea of how to communicate with Grafana using API calls
#And updating Ansible host list.

HOST = ''
API_KEY = ''


def get_datasources():
    headers = {'Authorization': 'Bearer %s' % (API_KEY,)}
    response = requests.get('%s/api/datasources' % (HOST,), headers=headers)
    response.raise_for_status()
    datasources = response.json()

    print(datasources)


def set_mysql_datasource(name,url,database,timeInterval):
    headers = {'Authorization': 'Bearer %s' % (API_KEY,),
               "Content-Type": "application/json",
               "Accept": "application/json"
               }

    new_datasource = {
        "name": name,
        "type": "mysql",
        "typeName": "MySQL",
        "typeLogoUrl": "public/app/plugins/datasource/mysql/img/mysql_logo.svg",
        "access": "proxy",
        "url": url,
        "user": "",
        "database": database,
        "secureJsonData": {
            "password": ""
        },
        "basicAuth": False,
        "isDefault": False,
        "jsonData": {"timeInterval": timeInterval},
        'readOnly': False
    }

    r = requests.post(url='%s/api/datasources' % (HOST,), headers=headers, data=json.dumps(new_datasource), verify=False)


def add_ansible_host(acc_code):

    command1 = "grep -n 'ansible_ssh_host=test1' /etc/ansible/hosts | tail -1"
    p = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in iter(p.stdout.readline, b''):
        result = line.decode('UTF-8')

    line_num = result.split(':',1)[0]
    remaining_line = result.split(':',1)[1]

    rpi_str = remaining_line.split(' ',1)[0]
    rpi_num = rpi_str.split('rpi',1)[1]

    new_rpi_num = str(int(rpi_num) + 1)
    new_line_num = str(int(line_num) + 1)

    line = "rpi" + new_rpi_num + " ansible_ssh_host=test1." + str(acc_code) + ".everywherewireless.com"
    command2 = "sed -i '%s i %s' /etc/ansible/hosts" % (new_line_num, line)

    p = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main():
    acc_code = input("Please enter the accounting code of the building (eg. TEST): ")

    print("\nUpdating Ansible Hosts File\n")
    add_ansible_host(acc_code)

    print("\nCreating Grafana Data Sources Next\n")
    print("Let's create the Diagnostics Data Source first\n")

    name = "test1." + str(acc_code) + ".everywherewireless.com - Diagnostics"
    url = "test1." + str(acc_code) + ".everywherewireless.com"
    database = ""
    timeinterval = "5m"

    set_mysql_datasource(name, url, database, timeinterval)

    print("\nDiagnostics Data Source has been created...Moving onto Bandwidth Data Source\n")

    name = "test1." + str(acc_code) + ".everywherewireless.com - Bandwidth"
    url = "test1." + str(acc_code) + ".everywherewireless.com"
    database = ""
    timeinterval = "1h"

    set_mysql_datasource(name, url, database, timeinterval)


if __name__ == '__main__':
    main()