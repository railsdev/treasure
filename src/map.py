import sys, urwid

class Map(urwid.BoxWidget):
   _selectable = True
   ignore_focus = True

   
   def __init__(self):
      self.terrain = [
"oooooooooooooooooooooooooooooooo",
"O                         |    O",
"O  |                      |    O",
"O  |                |     +-  -O",
"O  |--- ---         |          O",
"O         |         |          O",
"O         ----------|          O",
"O                              O",
"O         |                    O",
"oooooooooooooooooooooooooooooooo",
]
      self.cols = len(self.terrain[0])
      self.rows = len(self.terrain)
      self.man_row = 1
      self.man_col = 1

   def get_pref_col(self, size):
      "Returns the preferred screen column (for the cursor) as an integer or None."
      maxcol, maxrow = size
      # We don't have a cursor in the map...
      return None

   def keypress(self, size, key):
      maxcol, maxrow = size
      bound_row = min(maxrow, self.rows) - 1
      bound_col = min(maxcol, self.cols) - 1
      newrow = self.man_row
      newcol = self.man_col
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
      
      # You can't walk through walls!
      if self.terrain[newrow][newcol] != ' ':
         pass
      else:
         self.man_row = newrow
         self.man_col = newcol
         self._invalidate()

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
      if (self.man_row <= maxrow) and (self.man_col <= maxcol):
         lines[self.man_row] = lines[self.man_row][:self.man_col] + 'M' + lines[self.man_row][self.man_col + 1:]

      return urwid.TextCanvas(lines, maxcol=maxcol)

      
   
