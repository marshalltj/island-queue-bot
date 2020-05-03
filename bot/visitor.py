"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 2.0.0

visitor.py contains a class Visitor that connects a discord.User to a datetime object of when they join a queue for an Island
"""

import datetime

#Class that connects a discord.User to a timestamp
#Members: <user : discord.User> <trips : int> <timestamp : datetime.datetime> 
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
