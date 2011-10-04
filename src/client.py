#!/usr/bin/env python

import optparse, os, sys

#-------------------------------------------------------------------------------
# COMMAND-LINE PARSING

name = 'Uninitialized'
if __name__ == '__main__':
   parser = optparse.OptionParser(usage="treasure [options] (p1name)")
   parser.add_option('-s', '--server', dest='server', action='store', default='localhost', help='Domain name or IP address of server to connect to.  Defaults to localhost.')
   options, args = parser.parse_args()

   if len(args) > 0:
      name = args[0]
   else:
      parser.print_help()
      sys.exit(2)

import pygame, zmq
pygame.mixer.pre_init(44100, -16, 1, 2048)
pygame.init()
from treasure import *
import gfx, world

#-------------------------------------------------------------------------------
# GLOBALS

global p1          # Player 1 object (i.e. THIS player)
global sub_socket  # Subscription socket (receive events from server)
global push_socket # Push socket (send events to server)
global worldmap
worldmap = None

# Sounds
oink = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sound', 'oink.ogg'))
iamhere = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sound', 'iamhere.ogg'))
byebye = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sound', 'byebye.ogg'))
pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), 'sound', 'treasure_music.ogg'))

#-------------------------------------------------------------------------------
# ZMQ INITIALIZATION

context = zmq.Context()

# Socket to receive broadcasts from server
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://%s:5556" % options.server)
sub_socket.setsockopt(zmq.SUBSCRIBE, "all")
print "Connecting to server ...",
sys.stdout.flush()
sub_socket.recv()  # Will hang forever if no server.  Perhaps we should add a timeout.
print "success!"

# Socket to submit requests to server, receive replies
push_socket = context.socket(zmq.PUSH)
push_socket.connect("tcp://%s:5555" % options.server)


def send(command, **kwargs):
   """
   Send information to the server.
   
   command - A command string the server will accept.
   
   Depending upon the command, you will likely need additional named arguments.
   All named arguments will get passed through to the server.
   """
   global push_socket
   global p1
   cmd_dict = {
      'cmd':command,
      'player':p1,
      }
   cmd_dict.update(kwargs)
   push_socket.send_pyobj(cmd_dict)


# Function to receive info from server
def recv():
   global sub_socket
   try:
      msg = sub_socket.recv(flags=zmq.core.NOBLOCK)
   except zmq.core.error.ZMQError:
      pass
   else:
      sep = msg.find(':')
      to = msg[0:sep]
      obj = unpickle(msg[sep+1:])
      return obj

#-------------------------------------------------------------------------------
# GAME LOGIC

# Handle network traffic received on the subscription socket
def handle_network():
   global p1
   server_msg = recv()
   # Process input
   if server_msg:
      # Actor-based events
      if server_msg.has_key('actor'):
         actor = server_msg['actor']
         cmd = server_msg['cmd']
         if actor.uid == p1.uid:
            # We already know what we have done, so ignore it
            pass
         elif cmd == 'actor_enters':
            user_events.post('update_actor', actor=actor)
            user_events.post('redraw')
         elif cmd == 'actor_moved':
            user_events.post('update_actor', actor=actor)
         elif cmd == 'actor_exits':
            user_events.post('remove_actor', actor=actor)
            user_events.post('redraw')
         elif cmd == 'actor_speaks':
            print server_msg['chat_content']
      # Non-actor-based events
      elif server_msg.has_key('cmd'):
         cmd = server_msg['cmd']
         if cmd == 'server_quit':
            print 'Server has quit...stopping client.'
            quit()
         elif cmd == 'set_map':
            user_events.post('set_map', terrain=server_msg['terrain'])
         elif cmd == 'update_scoreboard':
            gfx.set_scoreboard(server_msg['scoreboard'])
            user_events.post('redraw')

def handle_keypress(event):
#   print pygame.key.name(event.key)
   global worldmap
   # Quit?
   if event.key == pygame.K_ESCAPE:
      quit()
   # Movement?
   if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
      # Figure out the direction
      direction = None
      if event.key == pygame.K_UP:
         direction = 'up'
      elif event.key == pygame.K_DOWN:
         direction = 'down'
      elif event.key == pygame.K_LEFT:
         direction = 'left'
      elif event.key == pygame.K_RIGHT:
         direction = 'right'
      # Is it a keydown or a keyup?
      if event.type == pygame.KEYDOWN:
         p1.keydown(direction)
      else:
         p1.keyup(direction)
   # Global toggles?
   if event.type == pygame.KEYDOWN:
      # Toggle music
      if event.key == pygame.K_m:
         if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
         else:
            pygame.mixer.music.play(-1)


def handle_graphics(window, redraw=False):
   global worldmap
   if redraw:
      # Black background
      window.fill(gfx.BLACK)
      # Center line
      pygame.draw.line(window, gfx.GREEN, (512,0), (512,512))
   # World map
   if worldmap:
      gfx.render_world(window, worldmap, redraw)
   # HUD
   gfx.render_text(window)
   pygame.display.flip()

def quit():
   send('disconnect')
   pygame.quit()
   sys.exit()

if __name__ == '__main__':
   # Player 1 (this client's main player)
   p1 = Player(1,1, name)
   sub_socket.setsockopt(zmq.SUBSCRIBE, p1.uid)

   send('connect')

   # set up the window
   window = pygame.display.set_mode((1024,512))
   pygame.display.set_caption('Treasure Hunter 0.4')
   pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
   pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
   pygame.event.set_blocked(pygame.MOUSEMOTION)

   pygame.mixer.music.set_volume(.2)
   pygame.mixer.music.play(-1)
   
   clock = pygame.time.Clock()
   delta = clock.tick(100)
   handle_graphics(window, redraw=True)
   while True:
      redraw = False
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            quit()
         elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            handle_keypress(event)
         elif event.type == pygame.ACTIVEEVENT:
            pass
         else:
            print "Unhandled event:", event
      
      while user_events.peek():
         event = user_events.get()
         if event.type == 'move':
            worldmap.move_player(event.direction)
         elif event.type == 'sound':
            if event.sound == 'oink':
               oink.play()
            elif event.sound == 'iamhere':
               iamhere.play()
            elif event.sound == 'byebye':
               byebye.play()
         elif event.type == 'redraw':
            redraw = True
         elif event.type == 'update_actor':
            if worldmap:
               worldmap.update_actor(event.actor)
         elif event.type == 'remove_actor':
            if worldmap:
               worldmap.remove_actor(event.actor)
            redraw = True
         elif event.type == 'set_map':
            worldmap = world.Map(p1, send, event.terrain)
            redraw = True
            
      if worldmap:
         worldmap.update(delta)
      handle_graphics(window, redraw)
      handle_network()
      delta = clock.tick(100)

