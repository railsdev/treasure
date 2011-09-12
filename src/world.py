import thing, sys, urwid

class Map(urwid.BoxWidget):
   _selectable = True
   ignore_focus = True

   
   def __init__(self, p1, send, terrain):
      self.send = send
      self.terrain = terrain
      self.cols = len(self.terrain[0])
      self.rows = len(self.terrain)
      self.cast = thing.Cast()
      self.p1 = p1
      self.cast.add_actor(p1)

   def get_pref_col(self, size):
      "Returns the preferred screen column (for the cursor) as an integer or None."
      maxcol, maxrow = size
      # We don't have a cursor in the map...
      return None
   
   def pack(self, size, focus=False):
      return (len(terrain[0]), len(terrain))

   def get_cursor_coords(self, size):
      return None

   def keypress(self, size, key):
      maxcol, maxrow = size
      bound_row = min(maxrow, self.rows) - 1
      bound_col = min(maxcol, self.cols) - 1
      newrow = self.p1.row
      newcol = self.p1.col
      if key == 'up':
         newrow -= 1
         if newrow < 0:
            newrow = 0
      elif key == 'down':
         newrow += 1
         if newrow > bound_row:
            newrow = bound_row
      elif key == 'right':
         newcol += 1
         if newcol > bound_col:
            newcol = bound_col
      elif key == 'left':
         newcol -= 1
         if newcol < 0:
            newcol = 0
      else:
         return key
      
      # You can't walk through solid objects!
      okay_to_move = True
      if self.terrain[newrow][newcol] == 'X':
         okay_to_move = False
      # You can't walk over other players!
      for actor in self.cast:
         if ((actor.uid != self.p1.uid) 
              and type(actor) == thing.Actor
              and actor.row == newrow 
              and actor.col == newcol):
            okay_to_move = False
      if okay_to_move:
         self.p1.row = newrow
         self.p1.col = newcol
         self._invalidate()
         self.send('move_actor')

   def render(self, size, focus=False):
      lines = list(self.terrain)
      maxcol, maxrow = size

      # Pad or trim rows of text, if necessary
      if maxrow > self.rows:
         # More rows than map
         lines.extend([' ' * self.cols for x in range(maxrow - self.rows)])
      elif maxrow < self.rows:
         # More map than rows
         lines = lines[:maxrow]

      # Pad or trim columns of text, if necessary
      if maxcol > self.cols:
         # More columns than map
         lines = [x + ' ' * (maxcol - self.cols) for x in lines]
      elif maxcol < self.cols:
         # More map than columns
         lines = [x[:maxcol] for x in lines]

      # Place the man
      for actor in self.cast:
         if (actor.row <= maxrow) and (actor.col <= maxcol):
            lines[actor.row] = lines[actor.row][:actor.col] + actor.symbol + lines[actor.row][actor.col + 1:]

      return urwid.TextCanvas(lines, maxcol=maxcol)

      
   def add_actor(self, actor):
      self.cast.add_actor(actor)
      self._invalidate()

   
   def rm_actor(self, actor):
      self.cast.rm_actor(actor)
      self._invalidate()
   
   def update_actor(self, actor):
      self.cast.update_actor(actor)
      self._invalidate()
