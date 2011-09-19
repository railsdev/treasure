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
import gfx, util, thing, world

#-------------------------------------------------------------------------------
# GLOBALS

global p1          # Player 1 object (i.e. THIS player)
global sub_socket  # Subscription socket (receive events from server)
global push_socket # Push socket (send events to server)
global worldmap
worldmap = None

# Sounds
oink = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'oink.ogg'))
pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), 'treasure_music.ogg'))

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
      'actor':p1,
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
      obj = util.unpickle(msg[sep+1:])
      return obj

#-------------------------------------------------------------------------------
# GAME LOGIC

# Handle network traffic received on the subscription socket
def handle_network():
   global p1
   global worldmap
   server_msg = recv()
   if server_msg:
      # Process input
      dirty = True
      # Actor-based events
      if server_msg.has_key('actor'):
         actor = server_msg['actor']
         cmd = server_msg['cmd']
         if actor.uid == p1.uid:
            # We already know what we have done, so ignore it
            dirty = False
         elif cmd in ['actor_enters', 'actor_moved']:
            if worldmap:
               worldmap.update_actor(actor)
         elif cmd == 'actor_exits':
            if worldmap:
               worldmap.rm_actor(actor)
         elif cmd == 'actor_speaks':
            print server_msg['chat_content']
      # Non-actor-based events
      elif server_msg.has_key('cmd'):
         cmd = server_msg['cmd']
         if cmd == 'set_map':
            worldmap = world.Map(p1, send, server_msg['terrain'])
         elif cmd == 'update_scoreboard':
            gfx.set_scoreboard(server_msg['scoreboard'])
      if dirty:
         # need to update the screen
         pass

def handle_keypress(event):
   global worldmap
   key = event.key
   if key == pygame.K_ESCAPE:
      quit()
   elif event.type == pygame.KEYDOWN:
      if key == pygame.K_m:
         if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
         else:
            pygame.mixer.music.play(-1)
      worldmap.keypress(event.key)
   elif event.type == pygame.KEYUP:
      pass
#   print pygame.key.name(key)


def handle_graphics(window):
   global worldmap
   # Black background
   window.fill(gfx.BLACK)
   # Center line
   pygame.draw.line(window, gfx.GREEN, (512,0), (512,512))
   # World map
   if worldmap:
      gfx.render_world(window, worldmap)
   # HUD
   gfx.render_text(window)
   pygame.display.flip()

def quit():
   send('disconnect')
   pygame.quit()
   sys.exit()

if __name__ == '__main__':
   # Player 1 (this client's main player)
   p1 = thing.Actor(1,1, uid=name)
   sub_socket.setsockopt(zmq.SUBSCRIBE, p1.uid)

   send('connect')

   # set up the window
   window = pygame.display.set_mode((1024,512))
   pygame.display.set_caption('Treasure Hunter 0.3')
   pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
   pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
   pygame.event.set_blocked(pygame.MOUSEMOTION)

   pygame.mixer.music.set_volume(.2)
   pygame.mixer.music.play(-1)
   
   clock = pygame.time.Clock()
   while True:
      handle_graphics(window)
      handle_network()
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            quit()
         elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            handle_keypress(event)
         elif event.type == pygame.ACTIVEEVENT:
            pass
         elif event.type == pygame.USEREVENT:
            if event.subtype == 'sound':
               if event.sound == 'oink':
                  oink.play()
         else:
            print "Unhandled event:", event
      clock.tick(100)

