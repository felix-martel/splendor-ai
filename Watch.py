import time

class Watch:
	globalWatch = None

	def __init__(self):
		self.time = time.time()
		self.dic = {}

	def start(self):
		self.time = time.time()

	def reset(self):
		self.dic = {}

	def loop(self,who=""):
		now = time.time()
		delta = now - self.time
		self.time = now
		if(who!=None and who!=""):
			self.add(who,delta)

	def add(self,who,delta):
		if(not(who in self.dic.keys())):
			self.dic[who]=0
		self.dic[who]+=delta

	def get(self,what):
		if(what in self.dic.keys()):
			return self.dic[what]
		return 0

	def __str__(self):
		result = ["-- Watch --"]
		total = sum(self.dic.values()) + 10**(-12)
		L = []
		for pair in self.dic.items():
			t = str(pair[0])
			t += " "*(24-len(t))+" : "
			t += str(round(pair[1],6))
			t += " "*(40-len(t)) + " (" + str(round(100*pair[1]/total,2)) + "%)"
			L.append((pair[1],t))
		L.sort(key = lambda x : -x[0])
		for l in L:
			result.append(l[1])
		return "\n".join(result)