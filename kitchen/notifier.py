from pykka import ThreadingActor
from threading import Thread, Event
import logging
from datetime import datetime
import json

class Notifier(Thread):
	def __init__(self, level, orderUpdatedCallback):
		Thread.__init__(self)
		self.logger = logging.getLogger(__name__)
		f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
		f_Handler.setLevel(level)
		f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
		f_Handler.setFormatter(f_Formart)
		self.logger.addHandler(f_Handler)
		self.stopped = Event()
		self.frontEndData = {'hot': dict(), 'cold': dict(), 'frozen': dict(), 'overflow': dict()}
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'Notifier has been created')
		self.orderUpdatedCallback = orderUpdatedCallback

	def applyData(self, renderInfo):
		if renderInfo.isDecayed or renderInfo.isPicked:
			try:
				del self.frontEndData[renderInfo.shelf][str(renderInfo.id)]
			except:
				pass
		else:
			self.frontEndData[renderInfo.shelf][str(renderInfo.id)] = json.dumps(renderInfo.__dict__)
		self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'frontEndData is ' + str(self.frontEndData))
		self.orderUpdatedCallback(self.frontEndData)

class NotifierActor(ThreadingActor):
	def __init__(self, pool, notifier):
		super().__init__()
		self.pool = pool
		self.notifier = notifier
		self.notifier.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'NotifierActor has been created')

	def on_receive(self, message):
		renderInfo = message['orderRenderInfo']
		self.notifier.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'order latest info received from orderActor, name is ' + renderInfo.name + ', order value is ' + str(renderInfo.value))
		self.notifier.applyData(renderInfo)
