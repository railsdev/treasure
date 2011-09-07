#!/usr/bin/env python

import time, zmq

context = zmq.Context()

# Socket to submit requests to server, receive replies
print "Connecting request socket to server."
req_socket = context.socket(zmq.REQ)
req_socket.connect("tcp://localhost:5555")

# Socket to receive broadcasts from server
print "Connect subscribe socket to server"
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://localhost:5556")
sub_socket.setsockopt(zmq.SUBSCRIBE, "")

# Client info
name = raw_input("What is your name? ")

print "Sending..."
req_socket.send_pyobj({'name':name})

# Get the reply.
reply = req_socket.recv_pyobj()
print "Received reply ", "[", reply, "]"

# Main Loop
while True:
   try:
      news = sub_socket.recv_pyobj(flags=zmq.core.NOBLOCK)
   except zmq.core.error.ZMQError:
      pass
   else:
      print "News from the server:", news
   time.sleep(.01)
