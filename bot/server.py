"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 2.0.0

server.py holds information about a discord guild and its associated island queues. 
"""

class Server:
	def __init__(self, guild, db):
		self.guild = guild
		self.islands = []

		cursor = db.cursor()

		sql = f"SELECT TurnipChannel, GeneralChannel, Timeout FROM Servers WHERE ID = {guild.id}"

		cursor.execute(sql)
		result = cursor.fetchone()

		self.turnipChannel = result[0]
		self.generalChannel = result[1]
		self.timeout = result[2]

		if self.timeout == None:
			self.timeout = 30

		cursor.close()
		db.close()

	def setTurnipChannel(self, channelId, db):
		cursor = db.cursor()

		sql = f"UPDATE Servers SET TurnipChannel = {channelId} WHERE ID = {self.guild.id}"

		cursor.execute(sql)

		db.commit()
		cursor.close()
		db.close()
		self.turnipChannel = channelId

	def setGeneralChannel(self, channelId, db):
		cursor = db.cursor()

		sql = f"UPDATE Servers SET GeneralChannel = {channelId} WHERE ID = {self.guild.id}"

		cursor.execute(sql)

		db.commit()
		cursor.close()
		db.close()
		self.generalChannel = channelId

	def setTimeout(self, time, db):
		cursor = db.cursor()

		sql = f"UPDATE Servers SET Timeout = {time} WHERE ID = {self.guild.id}"

		cursor.execute(sql)

		db.commit()
		cursor.close()
		db.close()
		self.timeout = time
