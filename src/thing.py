import random
random.seed()

class Actor(object):
   def __init__(self, row, col, uid=None, symbol=None):
      if uid and (type(uid) == str):
         self.uid = uid
         if not symbol:
            symbol = uid[0].upper()
      else:
         self.uid = str(id(self))
      self.row = row
      self.col = col
      self.symbol=symbol
      self.type = type

   def collide(self, other):
      return (other.row == self.row) and (other.col == self.col)
      
   def __repr__(self):
      return "<Actor %s %s@(%d,%d)>" % (self.uid, self.symbol, self.row, self.col)

class Pig(Actor):
   def __init__(self, terrain):
      self.terrain = terrain
      row, col = 0, 0
      while terrain[row][col] != ' ':
         row = random.choice(range(len(terrain)))
         col = random.choice(range(len(terrain[0])))
      super(Pig, self).__init__(
         row,
         col,
         uid='pig'+str(id(self)), symbol='p')

   def __repr__(self):
      return "<Pig %s %s@(%d,%d)>" % (self.uid, self.symbol, self.row, self.col)

   def move(self):
      direction = random.choice(['up', 'down', 'left', 'right'])
      # Attempt moving up to 5 times (we'll hit walls a lot)
      for i in range(5):
         newrow = self.row
         newcol = self.col
         if direction == 'up':
            newrow -= 1
         elif direction == 'down':
            newrow += 1
         elif direction == 'left':
            newcol -= 1
         elif direction == 'right':
            newcol += 1
         if (newrow < 0) or (newrow >= len(self.terrain)):
            continue
         if (newcol < 0) or (newcol >= len(self.terrain[0])):
            continue
         if (self.terrain[newrow][newcol] == 'X'):
            continue
         self.row = newrow
         self.col = newcol
         return True
      return False
         
      

class Cast(dict):
   # Ordered dictionary behavior (3 functions)
   def __init__(self, *args, **kwargs):
      self.index = 0
      self.order = []
      super(Cast, self).__init__(*args, **kwargs)
      
   def __setitem__(self, key, value):
      super(Cast, self).__setitem__(key, value)
      try:
         self.order.index(key)
      except:
         self.order.insert(0, key)
      
   def __delitem__(self, key):
      super(Cast, self).__delitem__(key)
      self.order.remove(key)
      
   # Iterator behavior (2 functions)
   # Return each actor (value), instead of the uid (key)
   def __iter__(self):
      self.index = 0
      return self
   
   def next(self):
      if self.index >= len(self.order) or self.index == -1:
         raise StopIteration
      actor = self[self.order[self.index]]
      self.index += 1
      return actor
   
   # Other functions
   def add_actor(self, actor):
      self.__setitem__(actor.uid, actor)
      print "Actors", self.order

   def rm_actor(self, actor):
      del self[actor.uid]
      self.index = -1
      print "Remaing actors", self.order
      
   def update_actor(self, actor):
      if not self.has_key(actor.uid):
         self.add_actor(actor)
      else:
         self[actor.uid] = actor
