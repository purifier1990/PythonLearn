from pykka import ThreadingActor
import random
from threading import Thread, Event
import logging
from datetime import datetime
from order import RenderDishInfo

class OrderDish(Thread):
	def __init__(self, order, shelfActor, overflowShelfActor, notifierActor, isOnOverflow, level):
		Thread.__init__(self)
		self.logger = logging.getLogger(__name__)
		f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
		f_Handler.setLevel(level)
		f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
		f_Handler.setFormatter(f_Formart)
		self.logger.addHandler(f_Handler)
		self.stopped = Event()
		self.order = order
		self.shelfLife = order.shelfLife
		self.decayRate = order.decayRate
		self.orderAge = 0
		self.shelfActor = shelfActor
		self.notifierActor = notifierActor
		self.overflowShelfActor = overflowShelfActor
		self.driverArriveTime = random.randint(2, 10)
		self.isOnOverflow = isOnOverflow
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order ' + str(self.order.id) + ', name is ' + self.order.name + ', has been created and started to decay itself, dirver arrived time is ' + str(self.driverArriveTime) + ' seconds from now. with shelf' + str(self.shelfActor) + ' On the overflowShelf: ' + str(self.isOnOverflow))
		self.start()

	def calcDecay(self):
		if self.isOnOverflow:
			value = (self.shelfLife - self.orderAge) - (self.decayRate * self.orderAge * 2)
		else:
			value = (self.shelfLife - self.orderAge) - (self.decayRate * self.orderAge)
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Lifetime: Order ' + str(self.order.id) + ', name is ' + self.order.name + ', order age is ' + str(self.orderAge) + ', value is ' + str(value) + ', driver arrived remaing seconds are ' + str(self.driverArriveTime) + ', on the overflowShelf: ' + str(self.isOnOverflow))
		return value

	def increaseAge(self):
		self.orderAge += 1

	def switchToShelf(self, shelfActor):
		self.isOnOverflow = False
		self.shelfActor = shelfActor
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Ordered ' + str(self.order.id) + ', name is ' + self.order.name +', has been moved from overflow shelf to ' + self.order.temp + ' shelf')

	def orderType(self):
		return self.order.temp

	def buildRenderInfo(self, isPicked, isDecayed):
		if self.isOnOverflow:
			return RenderDishInfo(self.order.id, self.order.name, 'overflow', self.calcDecay() / self.order.shelfLife, isPicked, isDecayed)
		return RenderDishInfo(self.order.id, self.order.name, self.orderType(), self.calcDecay() / self.order.shelfLife, isPicked, isDecayed)
		

	def run(self):
		while not self.stopped.wait(1):
			value = self.calcDecay()
			self.increaseAge()
			if value <= 0:
				self.stopped.set()
				if self.shelfActor != self.overflowShelfActor:
					self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Ordered ' + str(self.order.id) + ', name is ' + self.order.name +', has been decayed from ' + self.order.temp + ' shelf')
					self.shelfActor.tell({'source': 'orderDish', 'orderStatus': 'decayed', 'order': self.order})
				self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + self.order.temp + ' shelf has available slot to take orders from overflow shelf as order has decayed, sending message to it')
				self.overflowShelfActor.tell({'source': 'orderDish', 'orderStatus': 'decayed', 'shelf': self.shelfActor, 'order': self.order})
				self.notifierActor.tell({'source': 'OrderDish', 'orderRenderInfo': self.buildRenderInfo(False, True)})
			elif self.driverArriveTime == 0:
				self.stopped.set()
				if self.shelfActor != self.overflowShelfActor:
					self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Ordered ' + str(self.order.id) + ', name is ' + self.order.name +', has been pickup from ' + self.order.temp + ' shelf')
					self.shelfActor.tell({'source': 'orderDish', 'orderStatus': 'pickup', 'order': self.order})
				self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + self.order.temp + ' shelf has available slot to take orders from overflow shelf as order has been pickup, sending message to it')
				self.overflowShelfActor.tell({'source': 'orderDish', 'orderStatus': 'pickup', 'shelf': self.shelfActor, 'order': self.order})
				self.notifierActor.tell({'source': 'OrderDish', 'orderRenderInfo': self.buildRenderInfo(True, False)})
			else:
				self.notifierActor.tell({'source': 'OrderDish', 'orderRenderInfo': self.buildRenderInfo(False, False)})
			self.driverArriveTime -= 1
			


