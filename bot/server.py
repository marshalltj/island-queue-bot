"""
Animal Crossing New Horizons Island Queue Discord Bot
Author: Marshall Jankovsky
github.com/marshalltj/island-queue-bot

Version: 2.0.0

server.py holds information about a discord guild and its associated island queues. 
"""

class Server:
	def __init__(self, guild):
		self.guild = guild
		self.islands = []
		self.turnipChannel = None
		self.generalChannel = None
