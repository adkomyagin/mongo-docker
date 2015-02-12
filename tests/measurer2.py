import time
from timeit import default_timer as timer

def compute(times):
        n = len(times)
        if n < 2:
               raise ValueError('require at least two data points')
        c = sum(times)/float(n)
        ss = sum((x-c)**2 for x in times)
        pvar = ss/n # the population variance
        return [c,pvar**0.5]

class Measurer:
        times_sample = []
	times_test = []
	tmp_ts = 0

	def startSample(self):
		self.tmp_ts = timer()
		return self.tmp_ts

	def stopSample(self):
		ts = timer() - self.tmp_ts
		self.times_sample.append(ts)
		return ts

        def startTest(self):
                self.tmp_ts = timer()
                return self.tmp_ts

        def stopTest(self):
                ts = timer() - self.tmp_ts
                self.times_test.append(ts)
                return ts

	def check(self,acceptanceRatio=0.5,variabilityRatio=0.01):
                li_s = compute(self.times_sample)
                li_t = compute(self.times_test)
                
                if (li_s[1] / li_s[0]) > variabilityRatio:
                        print("Too high sample stdev " + str(li_s[1]) + ". Mean: " + str(li_s[0]))
                        return -1

                if (li_t[1] / li_t[0]) > variabilityRatio:
                        print("Too high test stdev " + str(li_t[1]) + ". Mean: " + str(li_t[0]))
                        return -1

                if abs(li_t[0] - li_s[0]) /  / li_s[0] > variabilityRatio:
                        print("Too high sample stdev " + str(li_s[1]) + ". Mean: " + str(li_s[0]))
                        return -1

    		n = len(self.times)
    		if n < 2:
        		raise ValueError('require at least two data points')
    		c = sum(self.times)/float(n)
    		ss = sum((x-c)**2 for x in self.times)
    		pvar = ss/n # the population variance
    		return [c,pvar**0.5]

	def check(self,mean,stdev):
		li = self.compute()
		if mean < li[0]:
			return -1
		if stdev < li[1]:
			return -1
		return 1
