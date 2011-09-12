#!/usr/bin/env python

import time, zmq
import thing

context = zmq.Context()

# Socket to reply to requests from individual clients
pull_socket = context.socket(zmq.PULL)
pull_socket.bind("tcp://*:5555")

# Socket to broadcast to all clients
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5556")

# Main Loop
cast = thing.Cast()
heartbeat = 0
while True:
   try:
      msg = pull_socket.recv_pyobj(flags=zmq.core.NOBLOCK)
   except zmq.core.error.ZMQError:
      pass
   else:
      # Process the request, and broadcast result
      print 'Processing', msg
      actor = msg['actor']
      if msg['cmd'] == 'connect':
         # Let the new client know about everyone else:
         for curr_actor in cast:
            pub_socket.send_pyobj(
               {'actor':curr_actor,
                'cmd':'actor_moved'})
         cast.add_actor(actor)
         pub_socket.send_pyobj(
            {'actor':actor,
             'cmd':'actor_enters'})
         
      elif msg['cmd'] == 'disconnect':
         pub_socket.send_pyobj(
            {'actor':actor,
             'cmd':'actor_exits'})
         cast.rm_actor(actor)
      elif msg['cmd'] == 'chat':
         pub_socket.send_pyobj(
            {'actor':actor,
             'cmd':'actor_speaks',
             'chat_content':msg['chat_content']})
      elif msg['cmd'] == 'move_actor':
         cast.update_actor(actor)
         pub_socket.send_pyobj(
            {'actor':actor,
             'cmd':'actor_moved'})
#   pub_socket.send_pyobj(heartbeat)
   heartbeat += 1
   time.sleep(.01)
