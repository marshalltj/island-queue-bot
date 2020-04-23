import datetime

class Visitor:
	def __init__(self, user, trips):
		self.user = user
		if trips == 0:
			self.trips = "?"
		else:
			self.trips = trips
		self.timestamp = datetime.datetime.now()

	def getTimeSpent(self):
		return divmod((datetime.datetime.now() - self.timestamp).seconds, 60)[0]

	def setTimestamp(self):
		self.timestamp = datetime.datetime.now()