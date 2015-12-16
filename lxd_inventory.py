#!/usr/bin/env python

# Author	:   thebinary <binary4bytes@gmail.com>
# Date		:   Sun Dec  6 16:11:36 NPT 2015
# Purpose	:   Ansible Dynamic Inventory for LXD containers


import os
import requests
import json
import sys
import argparse

parser = argparse.ArgumentParser(description='lxd_ansible_inventory arguments')
parser.add_argument('host', type=str, help='lxd hostname')
parser.add_argument('--list', action='store_true')
parser.add_argument('--host', action='store_true')
parser.add_argument('--create', action='store_true')
parser.add_argument('-p', '--port', type=int, help='lxd restapi port, default: 8443', default=8443)
parser.add_argument('-u', '--user', type=str, help='ansible ssh user in inventory', default="")

args = parser.parse_args()

ansible_ssh_user = args.user
lxd_host = args.host
lxd_port = args.port
lxd_link = 'https://' + lxd_host + ':' + str(lxd_port) + '/1.0'
lxd_containers = lxd_link + '/containers'

if args.create:
	argument="--create"

conf_dir = os.path.expanduser('~/.config/lxc')
crt = os.path.join(conf_dir, 'client.crt')
key = os.path.join(conf_dir, 'client.key')

groups = {'lxchosts': {'hosts': []}}
containers = {}

containers_reply = requests.get(lxd_containers, verify=False, cert=(crt, key)).text
containers_json = json.loads(containers_reply)
for container in containers_json['metadata']:
	container_name = container.replace( "/1.0/containers/", "")
	container_info = json.loads(requests.get(lxd_containers + "/" + container_name, verify=False, cert=(crt, key)).text)
	container_status =  container_info['metadata']['status']
	if ( container_status['status'] == 'Running' ):
		container_address = container_status['ips'][0]['address']
		containers[container_name] = container_address

if(argument == "--list" ):
	allhosts = containers.keys()
	groups['lxchosts']['hosts'] = allhosts
	print json.dumps(groups)
elif (argument == '--host' ):
	host_params = {}
	host = sys.argv[2]
	host_params['ansible_ssh_host'] = containers[host]
	host_params['ansible_ssh_user'] = ansible_ssh_user
	print json.dumps(host_params)
elif (argument == '--create' ):
	for host in containers.keys():
		host_params = {}
		host_params['ansible_ssh_host'] = containers[host]
		if ( ansible_ssh_user != "" ):
			host_params['ansible_ssh_user'] = ansible_ssh_user
		host_ansible_params=""
		for key in host_params:
			host_ansible_params = host_ansible_params + " " + key + "=" + host_params[key]
		print "%-35s%s" % (host, host_ansible_params)
elif (argument == '--lxcnames' ):
	for key in containers.keys():
		print key
