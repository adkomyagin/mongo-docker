import subprocess
import shlex
import time

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

hosts = {}

# create new system
deploy = {
"mongo_D1" : ("alex/mongod_2.7.8", "'--replSet xxx'"),
"mongo_D2" : ("alex/mongod_2.7.8", "'--replSet xxx'"),
"mongo_CFG" : ("alex/mongod_2.7.8", "''"),
"mongo_S1" : ("alex/mongos_2.7.8", "'--configdb mongo_CFG:27017'")
}

#host = "mongo_D1"
for host,opt in deploy.iteritems():
	res = docker_exec("docker run --dns '192.168.0.1' -h " + host + " --privileged -d " + opt[0] + " " + opt[1])
	if res != 0:
		print("Sucessfully started host " + host + " : " + res)
		hosts[host] = res
	else:
		print("Failed starting host " + host)

# initialize it

# run tests
time.sleep(10)

# cleanup
for host,cont_id in hosts.iteritems():
	print("Removing the host: " + host)
	res = docker_exec("docker rm -f " + cont_id)
	if res != 0:
        	print("Sucessfully removed host " + host + " : " + cont_id)
	else:
        	print("Failed removing host " + host + " : " + cont_id)
# run --dns "192.168.0.1" -h "mongo_D1" --privileged -d alex/mongod_2.7.8 '--replSet xxx'
#docker run --dns "192.168.0.1" -h "mongo_D2" --privileged -d alex/mongod_2.7.8 '--replSet xxx'
#docker run --dns "192.168.0.1" -h "mongo_CFG" --privileged -d alex/mongod_2.7.8 --quiet
#docker run --dns "192.168.0.1" -h "mongo_S1" --privileged -d alex/mongos_2.7.8 '--configdb mongo_CFG:27017' ""

#echo mongo mongo_S1  
