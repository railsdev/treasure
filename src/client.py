#!/usr/bin/env python

import optparse, time, urwid, zmq
import thing, world

parser = optparse.OptionParser()
options, args = parser.parse_args()

server_host = 'localhost'
if len(args) > 0:
   server_host = args[0]

context = zmq.Context()

# Socket to submit requests to server, receive replies
global push_socket
push_socket = context.socket(zmq.PUSH)
push_socket.connect("tcp://%s:5555" % server_host)

# Socket to receive broadcasts from server
global sub_socket
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://%s:5556" % server_host)
sub_socket.setsockopt(zmq.SUBSCRIBE, "")

def send_server(something):
   global push_socket
   push_socket.send_pyobj(something)

# Player 1 (this client's main player)
global p1
name = raw_input("What is your name? ")
p1 = thing.Actor(1,1, uid=name)

print "Sending..."
push_socket.send_pyobj({'actor':p1,'cmd':'connect'})

# Handle network traffic received on the subscription socket
def handle_network():
   global loop
   global frame
   global p1
   try:
      server_msg = sub_socket.recv_pyobj(flags=zmq.core.NOBLOCK)
   except zmq.core.error.ZMQError:
      pass
   else:
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
            map.update_actor(actor)
         elif cmd == 'actor_exits':
            map.rm_actor(actor)
         elif cmd == 'actor_speaks':
            frame.header = urwid.Filler(urwid.Text(server_msg['chat_content']))
      if dirty:
         loop.draw_screen()
   loop.event_loop.alarm(.01, handle_network)

# Handle any input that doesn't get handled by the focused widget
def main_input_handler(input):
   global push_socket
   global p1
   global frame
   if input == 'esc':
      push_socket.send_pyobj(
         {'cmd':'disconnect',
          'actor':p1})
      raise urwid.ExitMainLoop()
   if input == 'window resize':
      pass
   elif input == 'tab':
      frame.set_focus('footer')
   else:
      push_socket.send_pyobj(
         {'actor':p1,
          'cmd':'chat',
          'chat_content':input})

# Named color schemes we can use in our application
palette = [
   ('header', 'light red', 'black', 'standout')
]

class ChatEntry(urwid.Edit):
   def keypress(self, size, input):
      global push_socket
      global p1
      if input == 'enter':
         chat_content = self.get_edit_text()
         self.set_edit_text('')
         push_socket.send_pyobj(
            {'actor':p1,
             'cmd':'chat',
             'chat_content':chat_content})
      else:
         return super(ChatEntry, self).keypress(size, input)
         
      

global frame
global map
map = world.Map(p1, send_server)
frame = urwid.Frame(
   map, 
   header=urwid.AttrMap(urwid.Text('Treasure Hunter 0.1'), 'header'),
   footer=ChatEntry())

# Create the main loop
global loop
loop = urwid.MainLoop(frame, palette, unhandled_input=main_input_handler)
loop.event_loop.alarm(0, handle_network)
loop.run()
