#!/usr/bin/env python

import time, urwid, zmq

context = zmq.Context()

# Socket to submit requests to server, receive replies
global req_socket
req_socket = context.socket(zmq.REQ)
req_socket.connect("tcp://localhost:5555")

# Socket to receive broadcasts from server
global sub_socket
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://localhost:5556")
sub_socket.setsockopt(zmq.SUBSCRIBE, "")

# Client info
global name
name = raw_input("What is your name? ")

print "Sending..."
req_socket.send_pyobj({'name':name,'cmd':'connect'})

# Get the reply.
reply = req_socket.recv_pyobj()
print "Received reply ", "[", reply, "]"

# Handle network traffic received on the subscription socket
def handle_network():
   global loop
   global frame
   try:
      news = sub_socket.recv_pyobj(flags=zmq.core.NOBLOCK)
   except zmq.core.error.ZMQError:
      pass
   else:
      frame.get_body().body.contents.append(urwid.Text("%s" % news))
      loop.draw_screen()
   loop.event_loop.alarm(.01, handle_network)

# Handle any input that doesn't get handled by the focused widget
def main_input_handler(input):
   global req_socket
   global name
   if input == 'esc':
      req_socket.send_pyobj(
         {'name':name,
          'cmd':'disconnect'})
      req_socket.recv_pyobj()
      raise urwid.ExitMainLoop()
   else:
      req_socket.send_pyobj(
         {'name':name,
          'cmd':'chat',
          'chat_content':input})
      req_socket.recv_pyobj()

# Named color schemes we can use in our application
palette = [
   ('header', 'light red', 'black', 'standout')
]

class ChatEntry(urwid.Edit):
   def keypress(self, size, input):
      global req_socket
      global name
      if input == 'enter':
         chat_content = self.get_edit_text()
         self.set_edit_text('')
         req_socket.send_pyobj(
            {'name':name,
             'cmd':'chat',
             'chat_content':chat_content})
         req_socket.recv_pyobj()
      else:
         return super(ChatEntry, self).keypress(size, input)
         
      

global frame
frame = urwid.Frame(
   urwid.ListBox([]), 
   header=urwid.AttrMap(urwid.Text('Treasure Hunter 0.1'), 'header'),
   footer=ChatEntry())
frame.set_focus('footer')

# Create the main loop
global loop
loop = urwid.MainLoop(frame, palette, unhandled_input=main_input_handler)
loop.event_loop.alarm(0, handle_network)
loop.run()
