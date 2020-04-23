"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 1.0.0

island.py contains a class Island that tracks information about an island queue. 
"""

#Class that contains information about an island queue.
#Members: <owner : discord.User> <price : int> <users : [discord.User]> <code : str> <islandId : str> <queueSize : int>
class Island:
    def __init__(self, owner, price, users, code, islandId, queueSize):
        self.owner = owner
        self.price = price
        self.users = users
        self.code = code
        self.islandId = islandId
        self.queueSize = queueSize

    def getNumUsers(self):
        return len(self.users)

    def addUser(self, user):
        self.users.append(user)

    def removeUser(self, user):
        self.users.remove(user)

    def popUser(self, idx):
        return self.users.pop(idx)

    def getUserPositionInQueue(self, user):
        for i in range(self.getNumUsers()):
            if self.users[i] == user:
                return i
        return -1