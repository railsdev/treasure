#!/usr/bin/env python

import time, zmq

context = zmq.Context()

# Socket to reply to requests from individual clients
rep_socket = context.socket(zmq.REP)
rep_socket.bind("tcp://*:5555")

# Socket to broadcast to all clients
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5556")

# Main Loop
heartbeat = 0
while True:
   try:
      msg = rep_socket.recv_pyobj(flags=zmq.core.NOBLOCK)
   except zmq.core.error.ZMQError:
      pass
   else:
      rep_socket.send_pyobj(msg)
      print "Echoing object to all subscribers:", msg
      pub_socket.send_pyobj("%(name)s connected to the server!" % msg)
#   pub_socket.send_pyobj(heartbeat)
   heartbeat += 1
   time.sleep(.01)
