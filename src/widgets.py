import urwid

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
