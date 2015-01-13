import subprocess
import shlex
import time
import sys
import pymongo
from pymongo import MongoClient
import collections
import telnetlib 
import socket

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

def wait_until_up(host,port):
	print("Waiting for the " + host + " at " + str(port) + " to become available")
	while True:
		try:
#			print("Trying to reach " + host + " at " + str(port))
			tn = telnetlib.Telnet()
			tn.open(host,port,10)
			tn.close()
			break
		except socket.error:
			time.sleep(1)
                except socket.gaierror:
                        time.sleep(1)
		except:
			print "Unexpected error:", sys.exc_info()[0]
			raise

def wait_to_become_primary(host,port):
	client = MongoClient(host, port)
	print("Waiting for the " + host + " at " + str(port) + " to become PRIMARY")
	while (client.admin.command('ismaster', 1)["ismaster"] != True):
#		print("Waiting for " + host + " at " + str(port))
		time.sleep(1)

class MDocker:
	hosts = {}

	# deploys new nodes according to the spec, returns 1 on success
	def deploy(self, deploy):
		for host,opt in deploy.iteritems():
	        	res = docker_exec("docker run --dns '192.168.0.1' -h " + host + " --privileged -d " + opt[0] + " " + opt[1])
       		 	if res != 0:
                		print("Sucessfully started host " + host + " : " + res)
                		self.hosts[host] = res
				wait_until_up(host,opt[2])
				#time.sleep(6) #seems slow on my machine
        		else:
                		print("Failed starting host " + host)
				return 0
		return 1

	# cleanup
	def cleanup(self):
		for host,cont_id in self.hosts.iteritems():
       		 	print("Removing the host: " + host)
        		docker_exec("docker stop " + cont_id)
			res = docker_exec("docker rm " + cont_id)
        		if res != 0:
                		print("Sucessfully removed host " + host + " : " + cont_id)
        		else:
                		print("Failed removing host " + host + " : " + cont_id)

	def block(self, host):
        	docker_exec("docker exec " + self.hosts[host] + " /sbin/iptables -A INPUT -j DROP")
		docker_exec("docker exec " + self.hosts[host] + " /sbin/iptables -A OUTPUT -j DROP")

	def unblock(self, host):
        	docker_exec("docker exec " + self.hosts[host] + " /sbin/iptables -F")

        def local_mongo_shell(self, host, cmd):
                docker_exec("docker exec " + self.hosts[host] + " mongo --eval \"" + cmd + "\"")

