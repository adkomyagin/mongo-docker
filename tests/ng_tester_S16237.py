import mdocker
from mdocker import wait_until_up, wait_to_become_primary, MDocker
import pymongo
from pymongo import MongoClient
import collections
from timeit import default_timer as timer
from pymongo import ReadPreference
import time
import test

# create an instance of MDocker
docker = MDocker()

# create new system (image, params, mongo port)
deploy = collections.OrderedDict()
default_image = "test/mongodb_3.0.2"
deploy["mongo_D1"] = (default_image, "mongod --smallfiles --replSet xxx", 27017)
deploy["mongo_D2"] = (default_image, "mongod --smallfiles --replSet xxx", 27017)
deploy["mongo_CFG"] = (default_image, "mongod --smallfiles", 27017)
deploy["mongo_S1"] = (default_image, "mongos --configdb mongo_CFG:27017", 27017)

# deploy the system
res = docker.deploy(deploy)
if res != 1:
	print("Failed deploying. Aborting")
	docker.cleanup()
	sys.exit(2)

# initialize it
replSetConfig = {
     "_id" : "xxx",
     "members" : [
         {"_id" : 0, "host" : "mongo_D1", "priority" : 10},
         {"_id" : 1, "host" : "mongo_D2"}
     ]
}

print("Init replica set..")
client = MongoClient('mongo_D1', 27017)
client.admin.command('replSetInitiate', replSetConfig)

# we can use this fancy function to wait until the host becomes primary
wait_to_become_primary('mongo_D1', 27017)

print("Sharding the collection..")
client = MongoClient('mongo_S1', 27017, read_preference=ReadPreference.PRIMARY_PREFERRED)
client.admin.command('addShard', 'xxx/mongo_D1')
client.admin.command('enableSharding', 'test')
client.admin.command('shardCollection', 'test.test', key={'_id': 1})

client.admin.command('setParameter', 1, logLevel=5)

# TEST TIME!
data0 = []
data1 = []

fail0 = 0
fail1 = 0

print("Napping just in case...")
time.sleep(5)

client['test'].test.insert(deploy)

for x in range(0, 10000):
#	print("Running iteration " + str(x))
	start = timer()
        try:
	   val = client['test'].test.find_one()
        except:
           fail0 = fail0 + 1
	ts = timer() - start
        data0.append(ts)
        if (x%500 == 0): print str(x/100) + "% done"
#	print("TimeA: " + str(ts))

# Simulating the primary becoming a TCP black hole
docker.block("mongo_D1")
print("Napping 30 sec")
time.sleep(30)

for x in range(0, 10000):
#        print("Running iteration " + str(x))
        start = timer()
        try:
           val = client['test'].test.find_one()
        except:
           fail1 = fail1 + 1
        ts = timer() - start
        data1.append(ts)
        if (x%500 == 0): print str(x/100) + "% done"
#        print("TimeB: " + str(ts))

print "Fail stats: " + str(fail0) + " against " + str(fail1)


# discard first 1000 in each set
data0 = data0[1000:]
data1 = data1[1000:]

# compute metrics
l2,jm = test.compare_distributions(data0,data1,True)

# dump results
thefile = open("s5data0.txt", "w")
for item in data0:
  thefile.write("%s\n" % item)

thefile = open("s5data1.txt", "w")
for item in data1:
  thefile.write("%s\n" % item)

print("Done")

# cleanup
docker.cleanup()

# assert that one of criterias was a pass
assert (l2 or jm), "Konoe wara ficus paplatinus"
print "Test success"
