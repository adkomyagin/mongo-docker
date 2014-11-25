import subprocess
import shlex
import time
import sys
import pymongo
from pymongo import MongoClient
import collections
import telnetlib 
import socket

def wait_until_up(host,port):
	print("Waiting for the " + host + " at " + str(port) + " to become available")
	while True:
		try:
#			print("Trying to reach " + host + " at " + str(port))
			tn = telnetlib.Telnet()
			tn.open(host,port)
			tn.close()
			break
		except socket.error:
			time.sleep(1)
                except socket.gaierror:
                        time.sleep(1)
		except:
			print "Unexpected error:", sys.exc_info()[0]
			raise
#def wait_for_master(host):
	
# starts a new container and returns it's id or 0 if there was an error
def docker_exec(cmd):
	args = shlex.split(cmd)
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE);
	out, err = p.communicate()
	rc = p.returncode
	if rc != 0 :
		print("Command " + str(args) + " failed with rc " + str(rc) + " and error: " + err)
		return 0
	return out

# deploys new nodes according to the spec, returns 1 on success
def docker_deploy(deploy):
	global hosts
	for host,opt in deploy.iteritems():
        	res = docker_exec("docker run --dns '192.168.0.1' -h " + host + " --privileged -d " + opt[0] + " " + opt[1])
        	if res != 0:
                	print("Sucessfully started host " + host + " : " + res)
                	hosts[host] = res
			wait_until_up(host,opt[2])
			#time.sleep(6) #seems slow on my machine
        	else:
                	print("Failed starting host " + host)
			return 0
	return 1

# cleanup
def docker_cleanup():
	global hosts
	for host,cont_id in hosts.iteritems():
        	print("Removing the host: " + host)
        	res = docker_exec("docker rm -f " + cont_id)
        	if res != 0:
                	print("Sucessfully removed host " + host + " : " + cont_id)
        	else:
                	print("Failed removing host " + host + " : " + cont_id)

hosts = {}

# create new system (image, params, sleep time)
deploy = collections.OrderedDict()
deploy["mongo_D1"] = ("alex/mongod_1", "'--replSet xxx'", 27017)
deploy["mongo_D2"] = ("alex/mongod_1", "'--replSet xxx'", 27017)
deploy["mongo_CFG"] = ("alex/mongod_1", "''", 27017)
deploy["mongo_S1"] = ("alex/mongos_1", "'--configdb mongo_CFG:27017'", 27017)


#deploy = {
#"mongo_D1" : ("alex/mongod_2.7.8", "'--replSet xxx'"),
#"mongo_D2" : ("alex/mongod_2.7.8", "'--replSet xxx'"),
#"mongo_CFG" : ("alex/mongod_2.7.8", "''"),
#"mongo_S1" : ("alex/mongos_2.7.8", "'--configdb mongo_CFG:27017'")
#}

res = docker_deploy(deploy)
if res != 1:
	print("Failed deploying. Aborting")
	docker_cleanup()
	sys.exit(2)

# initialize it
replSetConfig = {
     "_id" : "xxx",
     "members" : [
         {"_id" : 0, "host" : "mongo_D1"},
         {"_id" : 1, "host" : "mongo_D2"}
     ]
}

print("Init replica set..")
client = MongoClient('mongo_D1', 27017)
client.admin.command('replSetInitiate', replSetConfig)

print("Napping just in case...")
time.sleep(10)

print("Sharding the collection..")
client = MongoClient('mongo_S1', 27017)
client.admin.command('addShard', 'xxx/mongo_D1')
client.admin.command('enableSharding', 'test')
client.admin.command('shardCollection', 'test.test', key={'_id': 1})

print("Napping just in case...")
time.sleep(5)

client['test'].test.insert(deploy)
print(client['test'].test.find_one())

print("Done")

# cleanup
docker_cleanup()

