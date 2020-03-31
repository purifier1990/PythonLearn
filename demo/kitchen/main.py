import threading
from orderReceiver import OrderSchedulerActor, OrderScheduler
from orderSimulator import OrderSimulatorActor, OrderSimulator
from shelf import HotShelf, HotShelfActor, ColdShelf, ColdShelfActor, FrozenShelf, FrozenShelfActor, OverflowShelf, OverflowShelfActor
from notifier import Notifier, NotifierActor
import logging
from flask import Flask, render_template

import os
import signal
import time

import pykka
import pykka.debug

from flask_socketio import SocketIO, emit
from flask import jsonify
import json

class ActorPool:
	pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

pool = ActorPool()

def OrderUpdatedCallback(data):
	socketio.emit('OrderUpdated', json.dumps(data))

notifier = Notifier(logging.INFO, OrderUpdatedCallback)
pool.notifierActor = NotifierActor.start(pool, notifier)

orderScheduler = OrderScheduler(15, 15, 15, 20, logging.INFO)
pool.orderSchedulerActor = OrderSchedulerActor.start(pool, orderScheduler, logging.INFO)

hotShelf = HotShelf(15, orderScheduler, logging.INFO)
pool.hotShelfActor = HotShelfActor.start(pool, hotShelf)

coldShelf = ColdShelf(15, orderScheduler, logging.INFO)
pool.coldShelfActor = ColdShelfActor.start(pool, coldShelf)

frozenShelf = FrozenShelf(15, orderScheduler, logging.INFO)
pool.frozenShelfActor = FrozenShelfActor.start(pool, frozenShelf)

overflowShelf = OverflowShelf(20, orderScheduler, logging.INFO)
pool.overflowShelfActor = OverflowShelfActor.start(pool, overflowShelf)

orderSimulator = OrderSimulator(pool.orderSchedulerActor, logging.INFO, 3.25)
pool.orderSimulatorActor = OrderSimulatorActor.start(pool, orderSimulator, logging.INFO)

logging.basicConfig(level=logging.DEBUG)
signal.signal(signal.SIGUSR1, pykka.debug.log_thread_tracebacks)
pid = os.getpid()
print('Making main thread relax; not block, not quit')
print('1) Use `kill -SIGUSR1 {:d}` to log thread tracebacks'.format(pid))
print('2) Then `kill {:d}` to terminate the process'.format(pid))

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@socketio.on('StartSimulation')
def StartSimulation(msg):
    orderSimulator.start()
    emit('StartSimulation', {'response': 'Simulation started'})
