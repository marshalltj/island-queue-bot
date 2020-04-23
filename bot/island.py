from visitor import Visitor

class Island:
    def __init__(self, owner, price, code, islandId, queueSize):
        self.owner = owner
        self.price = price
        self.code = code
        self.islandId = islandId
        self.queueSize = queueSize
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