#!/usr/bin/env python

import pygame, sys, zmq
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

pygame.init()

terrain = [
"                   XXX   X      ",
"                 X XXX X X XXXX ",
" X   X           X   X X X X    ",
"   X    X        XXX X X X X XXX",
"       X         X   X X X X    ",
"X X  X           X XXX X X XXXX ",
"          X      X     X   X    ",
"   X       X     XXXXXXXX XX XXX",
"         XXXX           X X     ",
"           X            X X     ",
"XXXX X    X                     ",
"      XX    XXX  XXX  X X  XXX  ",
"XXXX X        X  X X  X X  X    ",
"            XXX  X X  XXX  XXX  ",
"                                ",
"                                ",
"     XXXXXXXXXXXX XXXXX         ",
"     X          X     X         ",
"     X    X     X     X         ",
"     X    X           X         ",
"     X XXXX XXXXXXXXXXX    XXXXX",
"                                ",
"   XXXX                  XXXXX  ",
"XXXX                     X      ",
"     X XXXX        X X   X      ",
" XXXXX    X       XX XX  XX   XX",
"     XXXX X      XXX XXX  X     ",
"XXXX XX   X     XXXX XXXX X     ",
"   X XX XXXXXXX    X X    X     ",
" X      X                XXXXX  ",
"  XXXXXXXXXX XXXXXXXX    X      ",
"X                        X      ",
]

cast = thing.Cast()
cast.add_actor(thing.Pig(terrain))
cast.add_actor(thing.Pig(terrain))
cast.add_actor(thing.Pig(terrain))
cast.add_actor(thing.Pig(terrain))

def quit():
   send({'cmd':'server_quit'})
   print "Server exiting."
   pygame.quit()
   sys.exit()

# Main Loop
MAX_FPS = 200
heartbeat = 0
scoreboard = thing.ScoreBoard()
clock = pygame.time.Clock()
delta = clock.tick(MAX_FPS)
print "Server is running."
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
         scoreboard.modify_score(0, actor.uid)
         send({'cmd':'update_scoreboard',
               'scoreboard':scoreboard})
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
         scoreboard.rm_score(actor.uid)
         send({'cmd':'update_scoreboard',
               'scoreboard':scoreboard})
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
               print actor.uid, "caught", pig.uid, "for", pig.value, "points"
               scoreboard.modify_score(pig.value, actor.uid)
               send({'cmd':'update_scoreboard',
                     'scoreboard':scoreboard})
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
   if heartbeat % MAX_FPS == 0:
      send({'heartbeat':heartbeat})
   for pig in cast.update_pigs(delta):
      send({'actor':pig,
            'cmd':'actor_moved'})
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         quit()
      if event.type == pygame.KEYDOWN:
         if event.key == pygame.K_ESCAPE:
            quit()
   heartbeat += 1
   delta = clock.tick(MAX_FPS)
   
