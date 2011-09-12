#!/usr/bin/env python

import optparse, time, urwid, zmq
import util, thing, widgets, world

#-------------------------------------------------------------------------------
# COMMAND-LINE PARSING

server_host = 'localhost'
if __name__ == '__main__':
   parser = optparse.OptionParser()
   options, args = parser.parse_args()

   if len(args) > 0:
      server_host = args[0]

#-------------------------------------------------------------------------------
# GLOBALS

global frame ; frame = None
global loop  ; loop  = None
global map   ; map   = None

#-------------------------------------------------------------------------------
# ZMQ INITIALIZATION

context = zmq.Context()

# Socket to receive broadcasts from server
global sub_socket
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://%s:5556" % server_host)
sub_socket.setsockopt(zmq.SUBSCRIBE, "all")
print "Connecting to server..."
sub_socket.recv()

# Socket to submit requests to server, receive replies
global push_socket
push_socket = context.socket(zmq.PUSH)
push_socket.connect("tcp://%s:5555" % server_host)


# Function to send info to server
def send(cmd, **kwargs):
   global push_socket
   global p1
   d = {'actor':p1,
       'cmd':cmd}
   d.update(kwargs)
   push_socket.send_pyobj(d)


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
   global loop
   global frame
   global p1
   global map
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
            if map:
               map.update_actor(actor)
         elif cmd == 'actor_exits':
            if map:
               map.rm_actor(actor)
         elif cmd == 'actor_speaks':
            frame.header = urwid.Text(server_msg['chat_content'])
      # Non-actor-based events
      elif server_msg.has_key('cmd'):
         cmd = server_msg['cmd']
         if cmd == 'set_map':
            map = world.Map(p1, send, server_msg['terrain'])
            frame.set_body(map)
      if dirty:
         loop.draw_screen()
   loop.event_loop.alarm(.01, handle_network)


# Handle any input that doesn't get handled by the focused widget
def main_input_handler(input):
   global push_socket
   global p1
   global frame
   if input == 'esc':
      send('disconnect')
      raise urwid.ExitMainLoop()
   if input == 'window resize':
      pass
   elif input == 'tab':
      frame.set_focus('footer')
   else:
      send('chat', chat_content=input)
         
     
if __name__ == '__main__':
   # Named color schemes we can use in our application
   palette = [
      ('header', 'light red', 'black', 'standout')
   ]

   # Player 1 (this client's main player)
   global p1
   name = raw_input("What is your name? ")
   p1 = thing.Actor(1,1, uid=name)
   sub_socket.setsockopt(zmq.SUBSCRIBE, p1.uid)

   send('connect')

   frame = urwid.Frame(
      urwid.SolidFill('X'), 
      header=urwid.AttrMap(urwid.Text('Treasure Hunter 0.1'), 'header'),
      footer=widgets.ChatEntry())

   # Create the main loop
   loop = urwid.MainLoop(frame, palette, unhandled_input=main_input_handler)
   loop.event_loop.alarm(0, handle_network)
   loop.run()
