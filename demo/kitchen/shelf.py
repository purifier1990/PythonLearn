from pykka import ThreadingActor
import logging
from datetime import datetime
from orderDish import OrderDish

class HotShelf:
	def __init__(self, size, scheduler, level):
		self.logger = logging.getLogger(HotShelf.__name__)
		f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
		f_Handler.setLevel(level)
		f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
		f_Handler.setFormatter(f_Formart)
		self.logger.addHandler(f_Handler)
		self.size = size
		self.scheduler = scheduler
		self.orderDishes = dict()
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'HotShelf has been created, size is ' + str(self.size))

class HotShelfActor(ThreadingActor):
	def __init__(self, pool, hotShelf):
		super().__init__()
		self.pool = pool
		self.hotShelf = hotShelf
		self.hotShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'HotShelfActor has been created.')
		
	def on_receive(self, message):
		order = message['order']
		if message['source'] == 'schedulor':
			self.hotShelf.size -= 1
			message['cb']()
			self.hotShelf.orderDishes[order.id] = OrderDish(order, self.pool.hotShelfActor, self.pool.overflowShelfActor, self.pool.notifierActor, False, logging.INFO)
			self.hotShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order sent from scheduler has been received by hot shelf. id is ' + order.id + ', name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.hotShelf.size))
			#self.hotShelf.orderDishes[order.id].start()
		elif message['source'] == 'orderDish':
			self.hotShelf.size += 1
			self.hotShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order in hot shelf has been ' + message['orderStatus'] + ', name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.hotShelf.size))
			self.pool.orderSchedulerActor.tell({'source': 'Shelf', 'shelf': 'hot', 'order': message['order']})
			#del self.hotShelf.orderDishes[message['order'].id]

class ColdShelf:
	def __init__(self, size, scheduler, level):
		self.logger = logging.getLogger(ColdShelf.__name__)
		f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
		f_Handler.setLevel(level)
		f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
		f_Handler.setFormatter(f_Formart)
		self.logger.addHandler(f_Handler)
		self.size = size
		self.scheduler = scheduler
		self.orderDishes = dict()
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'ColdShelf has been created, size is ' + str(self.size))

class ColdShelfActor(ThreadingActor):
	def __init__(self, pool, coldShelf):
		super().__init__()
		self.pool = pool
		self.coldShelf = coldShelf
		self.coldShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'ColdShelfActor has been created.')
		
	def on_receive(self, message):
		order = message['order']
		if message['source'] == 'schedulor':
			self.coldShelf.size -= 1
			message['cb']()
			self.coldShelf.orderDishes[order.id] = OrderDish(order, self.pool.coldShelfActor, self.pool.overflowShelfActor, self.pool.notifierActor, False, logging.INFO)
			self.coldShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order sent from scheduler has been received by cold shelf. id is ' + order.id + ' name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.coldShelf.size))
			#self.coldShelf.orderDishes[order.id].start()
		elif message['source'] == 'orderDish':
			self.coldShelf.size += 1
			self.coldShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order in cold shelf has been ' + message['orderStatus'] + ', name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.coldShelf.size))
			self.pool.orderSchedulerActor.tell({'source': 'Shelf', 'shelf': 'cold', 'order': message['order']})
			#del self.coldShelf.orderDishes[message['order'].id]

class FrozenShelf:
	def __init__(self, size, scheduler, level):
		self.logger = logging.getLogger(FrozenShelf.__name__)
		f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
		f_Handler.setLevel(level)
		f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
		f_Handler.setFormatter(f_Formart)
		self.logger.addHandler(f_Handler)
		self.size = size
		self.scheduler = scheduler
		self.orderDishes = dict()
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'FrozenShelf has been created, size is ' + str(self.size))

class FrozenShelfActor(ThreadingActor):
	def __init__(self, pool, frozenShelf):
		super().__init__()
		self.pool = pool
		self.frozenShelf = frozenShelf
		self.frozenShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'FrozenShelf has been created.')
		
	def on_receive(self, message):
		order = message['order']
		if message['source'] == 'schedulor':
			self.frozenShelf.size -= 1
			message['cb']()
			self.frozenShelf.orderDishes[order.id] = OrderDish(order, self.pool.frozenShelfActor, self.pool.overflowShelfActor, self.pool.notifierActor, False, logging.INFO)
			self.frozenShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order sent from scheduler has been received by frozen shelf. id is ' + order.id + ' name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.frozenShelf.size))
			#self.frozenShelf.orderDishes[order.id].start()
		elif message['source'] == 'orderDish':
			self.frozenShelf.size += 1
			self.frozenShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order in frozen shelf has been ' + message['orderStatus'] + ', name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.frozenShelf.size))
			self.pool.orderSchedulerActor.tell({'source': 'Shelf', 'shelf': 'frozen', 'order': message['order']})
			#del self.frozenShelf.orderDishes[message['order'].id]

class OverflowShelf:
	def __init__(self, size, scheduler, level):
		self.logger = logging.getLogger(OverflowShelf.__name__)
		f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
		f_Handler.setLevel(level)
		f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
		f_Handler.setFormatter(f_Formart)
		self.logger.addHandler(f_Handler)
		self.size = size
		self.scheduler = scheduler
		self.orderDishes = dict()
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'OverflowShelf has been created, size is ' + str(self.size))

	def sendToSchedulerCallback(self):
		self.size += 1
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'Order in overflow shelf has been sent to other shelves, avaliable slots are ' + self.overflowShelf.size)

	def findAboutToDecay(self, temp):
		for key in self.orderDishes.keys():
			if self.orderDishes[key].orderType() == temp:
				return self.orderDishes[key]

class OverflowShelfActor(ThreadingActor):
	def __init__(self, pool, overflowShelf):
		super().__init__()
		self.pool = pool
		self.overflowShelf = overflowShelf
		self.overflowShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'OverflowShelf has been created.')
		
	def on_receive(self, message):
		order = message['order']
		if message['source'] == 'schedulor':
			self.overflowShelf.size -= 1
			message['cb']()
			if 'overflowShelfCallback' in message.keys():
				message['overflowShelfCallback']()
			self.overflowShelf.orderDishes[order.id] = OrderDish(order, self.pool.overflowShelfActor, self.pool.overflowShelfActor, self.pool.notifierActor, True, logging.INFO)
			self.overflowShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order sent from scheduler has been received by overflow shelf. id is ' + order.id + ' name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.overflowShelf.size))
			#self.overflowShelf.orderDishes[order.id].start()
		elif message['source'] == 'orderDish':
			shelf = message['shelf']
			if self is shelf:
				self.overflowShelf.size += 1
				self.overflowShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order in overflow shelf has been ' + message['orderStatus'] + ', name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp + ', avaliable slots are ' + str(self.overflowShelf.size))
				self.pool.orderSchedulerActor.tell({'source': 'Shelf', 'shelf': 'overflow', 'order': message['order']})  
				#del self.overflowShelf.orderDishes[message['order'].id]
			else:
				if shelf == self.pool.hotShelfActor:
					order = self.overflowShelf.findAboutToDecay('hot')
					if order != None:
						order.switchToShelf(shelf)
						self.overflowShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order in overflow shelf has sent to hot shelf as it is avaliable, name is' + order.name)
						self.pool.orderSchedulerActor.tell({'source': 'overflowShelf', 'order': order.order, 'overflowShelfCallback': self.overflowShelf.sendToSchedulerCallback})
				elif shelf == self.pool.coldShelfActor:
					order = self.overflowShelf.findAboutToDecay('cold')
					if order != None:
						order.switchToShelf(shelf)
						self.overflowShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order in overflow shelf has sent to cold shelf as it is avaliable, name is' + order.name)
						self.pool.orderSchedulerActor.tell({'source': 'overflowShelf', 'order': order.order, 'overflowShelfCallback': self.overflowShelf.sendToSchedulerCallback})
				elif shelf == self.pool.frozenShelfActor:
					order = self.overflowShelf.findAboutToDecay('frozen')
					if order != None:
						order.switchToShelf(shelf)
						self.overflowShelf.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order in overflow shelf has sent to frozen shelf as it is avaliable, name is' + order.name)
						self.pool.orderSchedulerActor.tell({'source': 'overflowShelf', 'order': order.order, 'overflowShelfCallback': self.overflowShelf.sendToSchedulerCallback})

	







