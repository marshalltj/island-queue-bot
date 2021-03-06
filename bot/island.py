"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 2.0.0

island.py contains a class Island that tracks information about an island queue. 
"""

import datetime
from visitor import Visitor

#Class that contains information about an island queue.
#Members: <owner : discord.User> <price : int>  <islandId : str> <guild : discord.Guild> <queueSize : int> <code : str> <timestamp : datetime.datetime> <visitors : [Visitor]>
class Island:
    def __init__(self, owner, price, islandId, guild):
        self.owner = owner
        self.price = price
        self.islandId = islandId
        self.guild = guild
        self.queueSize = None
        self.code = None
        self.timestamp = datetime.datetime.now()
        self.visitors = []

    def getNumVisitors(self):
        return len(self.visitors)

    def addVisitor(self, visitor, trips):
        self.visitors.append(Visitor(visitor, trips))

    def removeUser(self, user):
        for visitor in self.visitors:
            if visitor.user == user:
                self.visitors.remove(visitor)
                return True
        return False

    def popVisitor(self, idx):
        return self.visitors.pop(idx)

    def getUserPositionInQueue(self, user):
        for i in range(self.getNumVisitors()):
            if self.visitors[i].user == user:
                return i
        return -1

    def getAge(self):
        return divmod((datetime.datetime.now() - self.timestamp).seconds, 3600)[0]