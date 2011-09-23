#!/usr/bin/env python

import time, random, sys, zmq
from treasure import *
import level1, level2, level3

random.seed()

context = zmq.Context()

# Socket to reply to requests from individual clients
pull_socket = context.socket(zmq.PULL)
pull_socket.bind("tcp://*:5555")

# Socket to broadcast to all clients
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5556")

def send(pyobj, recipient='all'):
   pub_socket.send(recipient + ':' + pickle(pyobj))

levels = [level1, level2, level3]

terrain = random.choice(levels).terrain

cast = Cast()
cast.update(Pig(terrain))
cast.update(Pig(terrain))
cast.update(Pig(terrain))
cast.update(Pig(terrain))

def quit():
   send({'cmd':'server_quit'})
   print "Server exiting."
   sys.exit()

# Main Loop
MAX_FPS = 200
heartbeat = 0
scoreboard = ScoreBoard()
curr_time = last_time = time.time()
delta = 0.0
print "Server is running."
while True:
   # Loop time calculations
   last_time = curr_time
   curr_time = time.time()
   delta = curr_time - last_time
   try:
      msg = pull_socket.recv_pyobj(flags=zmq.core.NOBLOCK)
   except zmq.core.error.ZMQError:
      pass
   else:
      # Process the request, and broadcast result
      print 'Processing', msg
      player = msg['player']
      if msg['cmd'] == 'connect':
         # Give the client the terrain for the map
         print "Sending", player.name, "the terrain"
         send({'cmd':'set_map',
               'terrain':terrain}, recipient=player.uid)
         # Let the new client know about everyone else:
         scoreboard.modify_score(0, player.name)
         send({'cmd':'update_scoreboard',
               'scoreboard':scoreboard})
         for curr_actor in cast.actors_of_type(Player):
            send(
               {'actor':curr_actor,
                'cmd':'actor_moved'})
         cast.update(player)
         send(
            {'actor':player,
             'cmd':'actor_enters'})
         
      elif msg['cmd'] == 'disconnect':
         send(
            {'actor':player,
             'cmd':'actor_exits'})
         cast.remove(player)
         scoreboard.rm_score(player.name)
         send({'cmd':'update_scoreboard',
               'scoreboard':scoreboard})
      elif msg['cmd'] == 'chat':
         send(
            {'actor':player,
             'cmd':'actor_speaks',
             'chat_content':msg['chat_content']})
      elif msg['cmd'] == 'move_actor':
         cast.update(player)
         # Did I catch a pig?
         for pig in cast.actors_of_type(Pig):
            if player.collide(pig):
               print player.name, "caught", pig
               scoreboard.modify_score(pig.value, player.name)
               send({'cmd':'update_scoreboard',
                     'scoreboard':scoreboard})
               cast.remove(pig)
               send({'actor':pig,
                     'cmd':'actor_exits'})
               newpig = Pig(terrain)
               cast.update(newpig)
               send({'actor':newpig,
                     'cmd':'actor_enters'})
         send(
            {'actor':player,
             'cmd':'actor_moved'})
   # Check for win conditions
   high_score, name = scoreboard.high_score()
   if high_score >= 25:
      # round won announcement
      send({'cmd':'server_chat',
            'chat_content':'%s won the round with %d points!' % (name, high_score)})
      # reset scoreboard
      scoreboard.reset_scores()
      send({'cmd':'update_scoreboard',
           'scoreboard':scoreboard})
      # set new terrain
      terrain = random.choice(levels).terrain
      # reset the pigs
      for pig in cast.actors_of_type(Pig):
         pig.set_new_terrain(terrain)
         send({'actor':pig,
               'cmd':'actor_moved'})
      # send clients the new terrain
      send({'cmd':'set_map',
            'terrain':terrain})
      
   # Update pigs locations
   for pig in cast.update_pigs(delta):
      send({'actor':pig,
            'cmd':'actor_moved'})
   # Heartbeat
   if heartbeat % MAX_FPS == 0:
      send({'heartbeat':heartbeat})
   heartbeat += 1
   # Loop delay
   time.sleep(.005)
   
