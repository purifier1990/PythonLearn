from datetime import datetime
from pykka import ThreadingActor
import logging

class OrderScheduler:
    def __init__(self, hotShelfEmptySlot, coldShelfEmptySlot, frozenShelfEmptySlot, overflowShelfEmptySlot, level):
        self.logger = logging.getLogger(OrderScheduler.__name__)
        f_Handler = logging.FileHandler(datetime.now().strftime('./Logs/' + __name__ + '-%Y-%m-%d-%H-%M-%S.log'))
        f_Handler.setLevel(level)
        f_Formart = logging.Formatter('%(process)d-%(levelname)s-%(message)s')
        f_Handler.setFormatter(f_Formart)
        self.logger.addHandler(f_Handler)
        self.hotShelfEmptySlot = hotShelfEmptySlot
        self.coldShelfEmptySlot = coldShelfEmptySlot
        self.frozenShelfEmptySlot = frozenShelfEmptySlot
        self.overflowShelfEmptySlot = overflowShelfEmptySlot
        self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'OrderScheduler has been created. HotShelf size is ' + str(self.hotShelfEmptySlot) + ', ColdShelf size is ' + str(self.coldShelfEmptySlot) + ', FrozenShelf size is ' + str(self.frozenShelfEmptySlot) + ', OverflowShelf size is ' + str(self.overflowShelfEmptySlot))

    def sentHotOrderCallback(self):
        self.hotShelfEmptySlot -= 1
        self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'HotShelf has been assign one order, avaliable slots are ' + str(self.hotShelfEmptySlot))
    
    def sentColdOrderCallback(self):
        self.coldShelfEmptySlot -= 1
        self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'ColdShelf has been assign one order, avaliable slots are ' + str(self.coldShelfEmptySlot))

    def sentFrozenOrderCallback(self):
        self.frozenShelfEmptySlot -= 1
        self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'FrozenShelf has been assign one order, avaliable slots are ' + str(self.frozenShelfEmptySlot))
    
    def sentOverflowOrderCallback(self):
        self.overflowShelfEmptySlot -= 1
        self.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'OverflowShelf has been assign one order, avaliable slots are ' + str(self.overflowShelfEmptySlot))

class OrderSchedulerActor(ThreadingActor):
    def __init__(self, actorPool, orderScheduler, level):
        super().__init__()
        self.actorPool = actorPool
        self.orderScheduler = orderScheduler
        self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S    ') + 'OrderSchedulerActor has been created.')
        
    def on_receive(self, message):
        order = message['order']
        if message['source'] == 'Shelf':
            #self.dict[message['shelf']]()
            if message['shelf'] == 'hot':
                self.orderScheduler.hotShelfEmptySlot += 1
                self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'HotShelf has released one order, avaliable slots are ' + str(self.orderScheduler.hotShelfEmptySlot))
            elif message['shelf'] == 'cold':
                self.orderScheduler.coldShelfEmptySlot += 1
                self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'ColdShelf has released one order, avaliable slots are ' + str(self.orderScheduler.coldShelfEmptySlot))
            elif message['shelf'] == 'frozen':
                self.orderScheduler.frozenShelfEmptySlot += 1
                self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'FrozenShelf has released one order, avaliable slots are ' + str(self.orderScheduler.frozenShelfEmptySlot))
            else:
                self.orderScheduler.overflowShelfEmptySlot += 1
                self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'OverflowShelf has released one order, avaliable slots are ' + str(self.orderScheduler.overflowShelfEmptySlot))
        elif message['source'] == 'OrderSender':
            self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'OrderSchedulerActor has received one order from OrderSimulator. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
            if order.temp == 'hot':
                if self.orderScheduler.hotShelfEmptySlot > 0:
                    self.actorPool.hotShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentHotOrderCallback, 'order': order})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched to hot shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
                elif self.orderScheduler.overflowShelfEmptySlot > 0:
                    self.actorPool.overflowShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentOverflowOrderCallback, 'order': order})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched to overflow shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
                else:
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dumped as no avaliable shelf for it.')
            elif order.temp == 'cold':
                if self.orderScheduler.coldShelfEmptySlot > 0:
                    self.actorPool.coldShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentColdOrderCallback, 'order': order})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched to cold shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
                elif self.orderScheduler.overflowShelfEmptySlot > 0:
                    self.actorPool.overflowShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentOverflowOrderCallback, 'order': order})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched to oveflow shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
                else:
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dumped as no avaliable shelf for it.')
            elif order.temp == 'frozen':
                if self.orderScheduler.frozenShelfEmptySlot > 0:
                    self.actorPool.frozenShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentFrozenOrderCallback, 'order': order})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched to frozen shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
                elif self.orderScheduler.overflowShelfEmptySlot > 0:
                    self.actorPool.overflowShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentOverflowOrderCallback, 'order': order})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched to overflow shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
                else:
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dumped as no avaliable shelf for it.')
            else:
                self.orderScheduler.logger.warning(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'No shelf supports this kind of order. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
        elif message['source'] == 'overflowShelf':
            shelfTarget = message['order'].temp
            order = message['order']
            if shelfTarget == 'hot':
                if self.orderScheduler.hotShelfEmptySlot > 0:
                    self.actorPool.hotShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentHotOrderCallback, 'order': order, 'overflowShelfCallback': message['overflowShelfCallback']})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched from overflow Shelf to hot shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
            elif shelfTarget == 'cold':
                if self.orderScheduler.coldShelfEmptySlot > 0:
                    self.actorPool.coldShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentColdOrderCallback, 'order': order, 'overflowShelfCallback': message['overflowShelfCallback']})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched from overflow Shelf to cold shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)
            elif shelfTarget == 'frozen':
                if self.orderScheduler.frozenShelfEmptySlot > 0:
                    self.actorPool.frozenShelfActor.tell({'source': 'schedulor', 'cb': self.orderScheduler.sentFrozenOrderCallback, 'order': order, 'overflowShelfCallback': message['overflowShelfCallback']})
                    self.orderScheduler.logger.info(datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f    ') + 'Order has been dispatched from overflow Shelf to frozen shelf. name is' + order.name + ', shelfLife is ' + str(order.shelfLife) + ', decayRate is ' + str(order.decayRate) + ', temp is ' + order.temp)

