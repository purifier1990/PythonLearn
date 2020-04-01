import random
import math
import time
import json
from collections import namedtuple
from pykka import ThreadingActor
from orderReceiver import OrderSchedulerActor
from threading import Thread, Event
import logging
from order import Order
from datetime import datetime
import copy

class OrderSimulator(Thread):
	def __init__(self, orderScheduler, level, _lambda):
		Thread.__init__(self)
		self.logger = logging.getLogger(__name__)
		f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
		f_Handler.setLevel(level)
		f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
		f_Handler.setFormatter(f_Formart)
		self.logger.addHandler(f_Handler)
		self.orderScheduler = orderScheduler
		self.stopped = Event()
		self._lambda = _lambda
		with open('static/mockOrders.json') as f:
  			data = json.load(f)
		self.orders = data['orders']
		self.num_orders = len(self.orders)
		self.count = 0
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'OrderSimulator has been created. ')

	def run(self):
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'OrderSimulator has started. ')
		while not self.stopped.wait(1.0/self._lambda):
			selectedOrder = copy.deepcopy(self.orders[random.randint(0, self.num_orders - 1)])
			payload = Order(selectedOrder)
			self.orderScheduler.tell({'source': 'OrderSender', 'order': payload})
			self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been sent to Scheduler. id is ' + str(payload.id) + ' name is' + payload.name + ', shelfLife is ' + str(payload.shelfLife) + ', decayRate is ' + str(payload.decayRate) + ', temp is ' + payload.temp)

class OrderSimulatorActor(ThreadingActor):
	def __init__(self, actorPool, orderSimulator, level):
		super().__init__()
		self.actorPoor = actorPool
		self.orderSimulator = orderSimulator
		self.orderSimulator.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'OrderSimulatorActor has been created.')

	




