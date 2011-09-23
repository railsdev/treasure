import cPickle, cStringIO, random
random.seed()

#------------------------------------------------------------------------------
# User Event Classes (use the global user_events object instantiated below)

class Event(object):
   def __init__(self, type, **kwargs):
      self.type = type
      for key in kwargs:
         setattr(self, key, kwargs[key])

class UserEvents(object):
   def __init__(self):
      self.events = []

   def post(self, type, **kwargs):
      self.events.insert(0, Event(type, **kwargs))

   def get(self):
      if self.events:
         return self.events.pop()
      else:
         return None

   def peek(self):
      return len(self.events)

user_events = UserEvents()

#-------------------------------------------------------------------------------
# Network helper functions

def pickle(some_obj):
   """
   Take an arbitrary object and return a string with the pickled representation 
   of it.
   """
   pickled_str_io = cStringIO.StringIO()
   cPickle.dump(some_obj, pickled_str_io)
   pickled_str = pickled_str_io.getvalue()
   return pickled_str


def unpickle(pickled_str):
   """
   Take a string with the pickled representation of an object, unpickle it and
   return the object.
   """
   pickled_str_io = cStringIO.StringIO(pickled_str)
   return cPickle.load(pickled_str_io)

#-------------------------------------------------------------------------------
# Game Objects

class Actor(object):
   def __init__(self, row, col):
      self.set_location(row, col, init=True)
      self.uid = str(id(self))
      

   def collide(self, other):
      if other == self:
         return False
      if (type(other) == tuple) or (type(other) == list):
         other_row = other[0]
         other_col = other[1]
      else:
         other_row = other.row
         other_col = other.col
      return (other_row == self.row) and (other_col == self.col)


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
      return "<Actor %s (%d,%d)>" % (self.uid, self.row, self.col)


   
class Player(Actor):
   MOVE_DELAY = 150
   def __init__(self, row, col, name, symbol=None):
      super(Player, self).__init__(row, col)
      if name and (type(name) == str):
         self.name = name
      else:
         self.name = 'Player' + self.uid
      if not symbol:
         symbol = name[0].upper()
      self.symbol=symbol
      self.direction_stack = []
      self.timer = 0


   def __repr__(self):
      return "<Player %s/%s (%d,%d)>" % (self.name, self.uid, self.row, self.col)


   def keydown(self, direction):
      self.direction_stack.insert(0, direction)


   def keyup(self, direction):      
      try:
         self.direction_stack.remove(direction)
      except ValueError:
         pass


   def update(self, delta):
      # Update the move timer
      if self.timer:
         self.timer -= delta
         if self.timer < 0:
            self.timer = 0
      # Can we move now?
      if (self.timer == 0) and self.direction_stack:
         user_events.post('move', direction=self.direction_stack[0])
         self.timer = self.MOVE_DELAY


   def reset_move_timer(self):
      self.timer = 0
   
   
   def clone(self, other):
      self.row             = other.row
      self.col             = other.col
      self.old_row         = other.old_row
      self.old_col         = other.old_col
      self.symbol          = other.symbol
      self.direction_stack = other.direction_stack
      self.timer           = other.timer



class Pig(Actor):
   PIG_MOVE_DELAY = 0.500
   def __init__(self, terrain):
      # Pick random starting location...that's not in a wall.
      row = random.choice(range(len(terrain)))
      col = random.choice(range(len(terrain[0])))
      while terrain[row][col] != ' ':
         row = random.choice(range(len(terrain)))
         col = random.choice(range(len(terrain[0])))
      # Now that we have row and col, initialize superclass stuff
      super(Pig, self).__init__(row, col)
      # Pig-specific stuff...
      self.terrain = terrain
      self.move_timer = self.PIG_MOVE_DELAY
      self.value = random.choice(range(1,4))


   def __repr__(self):
      return "<Pig %s (%d,%d) %d pts>" % (self.uid, self.row, self.col, self.value)


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


   def clone(self, other):
      self.row        = other.row
      self.col        = other.col
      self.old_row    = other.old_row
      self.old_col    = other.old_col
      self.terrain    = other.terrain
      self.move_timer = other.move_timer
      self.value      = other.value
      

class Cast(object):
   def __init__(self):
      self.members = {
         Player : [],
         Pig    : [],
         }


   def actors_of_type(self, actor_type):
      if self.members.has_key(actor_type):
         return self.members[actor_type]
      else:
         return []


   def remove(self, actor):
      reference = self.find_actor(actor)
      if reference:
         self.members[type(actor)].remove(reference)


   def find_actor(self, actor):
      for reference in self.members[type(actor)]:
         if actor.uid == reference.uid:
            return reference
      return None


   def update(self, actor):
      reference = self.find_actor(actor)
      if reference:
         reference.clone(actor)
      else:
         self.members[type(actor)].append(actor)


   def occupies(self, row, col):
      other = Actor(row, col)
      for player in self.members[Player]:
         if player.collide(other):
            return True
      for pig in self.members[Pig]:
         if pig.collide(other):
            return True
      return False


   def has_actor(self, actor):
      match_list = [x for x in self.members[type(actor)] if actor.uid == x.uid]
      if match_list:
         return True
      return False


   def update_pigs(self, delta):
      moved = []
      for pig in self.members[Pig]:
         if pig.update(delta, self):
            moved.append(pig)
      return moved


class ScoreBoard(object):
   def __init__(self):
      self.scores = {}


   # Iterator functions
   def __iter__(self):
      self.sorted_list = [x for x in sorted(self.scores.iteritems(), key=lambda (k,v): (v,k))]
      return self


   def next(self):
      """Returns (name, score)"""
      if len(self.sorted_list) > 0:
         return self.sorted_list.pop()
      else:
         raise StopIteration
   # End iterator functions
      
   def modify_score(self, amount, name):
      if self.scores.has_key(name):
         self.scores[name] += amount
      else:
         self.scores[name] = amount


   def rm_score(self, name):
      if self.scores.has_key(name):
         del(self.scores[name])
         

