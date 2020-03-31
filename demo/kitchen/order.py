from datetime import datetime
import uuid

class Order():
	def __init__(self, order):
		self.__dict__ = order
		self.id = str(uuid.uuid4())

class RenderDishInfo():
	def  __init__(self, id, name, shelf, value, isPicked, isDecayed):
		self.id = id
		self.name = name
		self.shelf = shelf
		self.value = value
		self.isPicked = isPicked
		self.isDecayed = isDecayed