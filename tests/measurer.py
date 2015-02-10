import time
from timeit import default_timer as timer

class Measurer:
        times = []
	tmp_ts = 0

	def start(self):
		self.tmp_ts = timer()
		return self.tmp_ts

	def stop(self):
		ts = timer() - self.tmp_ts
		self.times.append(ts)
		return ts

	def compute(self):
    		n = len(self.times)
    		if n < 2:
        		raise ValueError('require at least two data points')
    		c = sum(self.times)/float(n)
    		ss = sum((x-c)**2 for x in self.times)
    		pvar = ss/n # the population variance
    		return [c,pvar**0.5]

