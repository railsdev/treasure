#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, zmq
import thing, util

context = zmq.Context()

# Socket to reply to requests from individual clients
pull_socket = context.socket(zmq.PULL)
pull_socket.bind("tcp://*:5555")

# Socket to broadcast to all clients
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5556")

def send(pyobj, recipient='all'):
   pub_socket.send(recipient + ':' + util.pickle(pyobj))

terrain = [
"X                              X",
"                 X XXX          ",
"                 X   X          ",
"       X X       XXX X          ",
"        X            X          ",
"       X X         XXX          ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"     XXXXXXXXXXXXXXXXXX         ",
"          X     X               ",
"          X     X               ",
"          X     X               ",
"          X     X               ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"X                              X",
]

cast = thing.Cast()
cast.add_actor(thing.Pig(terrain))
cast.add_actor(thing.Pig(terrain))
cast.add_actor(thing.Pig(terrain))
cast.add_actor(thing.Pig(terrain))

# Main Loop
heartbeat = 0
pig_delay = 75 
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
         # Give the client the terrain for the map
         print "Sending", actor.uid, "the terrain"
         send({'cmd':'set_map',
               'terrain':terrain}, recipient=actor.uid)
         # Let the new client know about everyone else:
         for curr_actor in cast:
            send(
               {'actor':curr_actor,
                'cmd':'actor_moved'})
         cast.add_actor(actor)
         send(
            {'actor':actor,
             'cmd':'actor_enters'})
         
      elif msg['cmd'] == 'disconnect':
         send(
            {'actor':actor,
             'cmd':'actor_exits'})
         cast.rm_actor(actor)
      elif msg['cmd'] == 'chat':
         send(
            {'actor':actor,
             'cmd':'actor_speaks',
             'chat_content':msg['chat_content']})
      elif msg['cmd'] == 'move_actor':
         cast.update_actor(actor)
         # Did I catch a pig?
         for pig in cast:
            if (type(pig) == thing.Pig) and actor.collide(pig):
               print actor.uid, "caught", pig.uid
               cast.rm_actor(pig)
               send({'actor':pig,
                     'cmd':'actor_exits'})
               newpig = thing.Pig(terrain)
               cast.add_actor(newpig)
               send({'actor':newpig,
                     'cmd':'actor_enters'})
         send(
            {'actor':actor,
             'cmd':'actor_moved'})
   if heartbeat % 100 == 0:
      send({'heartbeat':heartbeat})
   if heartbeat % pig_delay == 0:
      for pig in cast:
         if type(pig) == thing.Pig:
            if pig.move(cast=cast):
               send({'actor':pig,
                     'cmd':'actor_moved'})
   heartbeat += 1
   time.sleep(.01)
