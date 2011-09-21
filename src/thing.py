import copy, pygame, random
random.seed()

class Actor(object):
   MOVE_DELAY = 150
   def __init__(self, row, col, uid=None, symbol=None):
      if uid and (type(uid) == str):
         self.uid = uid
         if not symbol:
            symbol = uid[0].upper()
      else:
         self.uid = str(id(self))
      self.set_location(row, col, init=True)
      self.symbol=symbol
      self.type = type
      self.direction_stack = []
      self.timer = 0

   def control(self, event):
      # Movement
      if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
         if event.type == pygame.KEYDOWN:
            self.direction_stack.insert(0, event.key)
         elif event.type == pygame.KEYUP:
            try:
               self.direction_stack.remove(event.key)
            except ValueError:
               pass
      # If we think we're stopped, but there's 

   def update(self, delta):
      # Update the move timer
      if self.timer:
         self.timer -= delta
         if self.timer < 0:
            self.timer = 0
      # Can we move now?
      if (self.timer == 0) and self.direction_stack:
         pygame.event.post(pygame.event.Event(pygame.USEREVENT, subtype='move', direction=self.direction_stack[0]))
         self.timer = self.MOVE_DELAY

   def reset_move_timer(self):
      self.timer = 0

   def collide(self, other):
      return (other.row == self.row) and (other.col == self.col)

   def set_location(self, row, col, init=False):
      if init:
         self.clear_old_location()
      else:
         self.old_row = self.row
         self.old_col = self.col
      self.row = row
      self.col = col

   def clear_old_location(self):
      self.old_row = None
      self.old_col = None
      
   def __repr__(self):
      return "<Actor %s %s@(%d,%d)>" % (self.uid, self.symbol, self.row, self.col)

class Pig(Actor):
   PIG_MOVE_DELAY = 500
   def __init__(self, terrain):
      self.terrain = terrain
      row = random.choice(range(len(terrain)))
      col = random.choice(range(len(terrain[0])))
      while terrain[row][col] != ' ':
         row = random.choice(range(len(terrain)))
         col = random.choice(range(len(terrain[0])))
      super(Pig, self).__init__(
         row,
         col,
         uid='pig'+str(id(self)), symbol='p')
      self.move_timer = self.PIG_MOVE_DELAY
      self.value = random.choice(range(1,4))

   def __repr__(self):
      return "<Pig %s %s@(%d,%d)>" % (self.uid, self.symbol, self.row, self.col)

   def update(self, delta, cast):
      self.move_timer -= delta
      if self.move_timer < 0:
         self.move_timer = self.PIG_MOVE_DELAY
         self.move(cast)
         return True

   def move(self, cast):
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
         if cast.occupies(newrow, newcol):
            continue
#          print self.uid, "moving from (%d,%d) to (%d,%d)" % (self.row, self.col, newrow, newcol)
         self.set_location(newrow, newcol)
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
      return copy.deepcopy(self)
   
   def next(self):
      if self.index >= len(self.order) or self.index == -1:
         raise StopIteration
      actor = self[self.order[self.index]]
      self.index += 1
      return actor
   
   # Other functions
   def add_actor(self, actor):
      self.__setitem__(actor.uid, actor)

   def rm_actor(self, actor):
      del self[actor.uid]
      self.index = -1
      
   def update_actor(self, actor):
      if not self.has_key(actor.uid):
         self.add_actor(actor)
      else:
         self[actor.uid] = actor

   def occupies(self, row, col):
      for key in self.keys():
         if (self[key].row == row) and (self[key].col == col):
            return True
      return False

   def has_actor(self, actor):
      return self.has_key(actor.uid)

   def update_pigs(self, delta):
      moved = []
      for uid in self.order:
         curr_pig = self[uid]
         if type(curr_pig) != Pig:
            continue
         if curr_pig.update(delta, self):
            moved.append(curr_pig)
      return moved


class ScoreBoard(object):
   def __init__(self):
      self.scores = {}

   def modify_score(self, amount, uid):
      if self.scores.has_key(uid):
         self.scores[uid] += amount
      else:
         self.scores[uid] = amount

   def rm_score(self, uid):
      if self.scores.has_key(uid):
         del(self.scores[uid])
         
   # Iterator functions
   def __iter__(self):
      self.sorted_list = [x for x in sorted(self.scores.iteritems(), key=lambda (k,v): (v,k))]
      return self


   def next(self):
      """Returns (uid, score)"""
      if len(self.sorted_list) > 0:
         return self.sorted_list.pop()
      else:
         raise StopIteration
