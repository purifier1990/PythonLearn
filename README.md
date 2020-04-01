# Kitchen order simulation

This is a project for a web App that runs under flask to simulate order dispatch process.

## Architecture

It's based on an actor model architecture, which is like producer and consumer pattern, each part in this system is built upon an actor provided by pykka.

* 1st producer is order simulator, it provides the real life order sending to the scheduler.

* 2nd producer is scheduler, it also servers as order simulater's consumer, its functionality is to monitor order sending from the order simulator and based on order's temp to decide to send to its shelf accordingly, and when the target shelf is full, it tries overflow shelf, and when overflow shelf is full, just simply dumps the order, reasons are because I observed the mocked json order, and found the orders are almost not to be wasted itself since the shelflife is a very big number, also, as I am the first time doing the backend server development with python, when I choose to use pykka, the downside for this framework is that it can't give me capbility to dump the dispatched order.

* 3rd producers are 4 shelves, they monitor the order dispatched from scheduler, and created the order thread to do the self maintain status for each order, also update order status when it's decayed or picked up, shelves will notify scheduler to be ready to take more order, and in the meantime, except overflow shelf, other shelves will also notify overflow shelf to ask for orders from overflow shelf if it has orders.

* 4th producer is notifier, this serves to communicate with front end web site with websocket to update the displayed order information, it monitored each order thread's 'pick up' and 'decay' message to update the information accordingly.

## Prerequisites

Flask, SocketIO, pykka
No idea if the python venv can make it have already included the dependencies.

### Installing

under project folder, run
 ```
 ./venv/bin/activate
 ```
to enable venv, then with command under 'kitchen' folder
```
flask run
```
to start the server, then we can use local ip printed by command line tool to open the web site, once it rendered, click the 'start simulation' button, then you can see the orders json updated per second.

## Unit test

I haven't done this part, as I am struggling writing python server code, and have no idea on how to test each module, I do find some unit test information for python such as pytest, but writing project running code has taken me lots of time, and I don't have confidence on learning another tool to write unit test for my immature code.

Current code has difficulty doing unit test due to pykka limitation, its design way is that whenever someone wants to receive message, the caller to send message is receiver itself, which leads to each producer has to hold a reference for its consumer, and another issue is pykka actor can be only initialized by its 'start' method, and this method only returns an actor reference instead of class instance, so makes me hard to freely initialize all the stuffs, kind of making the whole system strongly coupled with each other.

## For the order movement to overflow shelf

My logic here is everytime the scheduler receives an order, it will detect the temp which is 'hot', 'cold' and 'frozen', and then looks for its own model to see if targeted shelf is OK to handle this order or not, and if not, the scheduler will see if overflow shelf has empty slot to hanlde this order or not, and if it's still not, this order will be dropped. For example, if scheduler receives one order of 'hot' and 'hot' shelf still has empty slot to handle more orders, then scheduler will dispatch this order to 'hot' shelf, otherwise, if 'overflow' shelf has empty slot to handle more orders, scheduler will dispatch this order to 'overflow' shelf.

Another logic is when other shelves have ordered either decayed or picked up, they will send messages to scheduler and 'overflow' shelf to ask for more orders to handle, and if this time overflow has some orders matched with other idle shelf, 'overflow' shelf will handle related order to its matching shelf to decrease the decay speed.

## Known issues

* pykka seems to have a thread race condition issue when the message is sending too frequently.
* No error handling for this server, as it runs locally, no network call happens, so I don't know if there are some error cases I need to take account.
* Front end directly shows the full json as raw string, but the spec mentions only normalized value and order name are needed to display, I didn't take time on developing web site.

## Future enhancement

* Should use a different architecture to support the waste strategy design, which is schedulor will hold all the order information and when a new order comes and need to drop one order, system can use either AI or other smart strategy to decide which order to be dropped.
* Due to not familiar with Python, so the code written is style is really bad and hard to scale if shelf and order style are extending. Suppose the server should have a configure file and server administrator can type any parameters either new added or modified old one based on valid server rule, then the server can be configured to be run with different shelf style, order style, order decay way and even front end received data.
* For the extra credit, I actually implemented a function for the order thread itself to maintain its own decay formula and status, but for this project so far, I only give it as its own class function, the decay function can be refactored to be a callback passed into order class whenever it is initialized so that the decay formula can be dynamically adpated.
