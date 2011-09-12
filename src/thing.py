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
      
   def __repr__(self):
      return "<Actor %s %s@(%d,%d)>" % (self.uid, self.symbol, self.row, self.col)

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
         self.order.append(key)
      
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
      print self.order

   def rm_actor(self, actor):
      del self[actor.uid]
      self.index = -1
      print self.order
      
   def update_actor(self, actor):
      if not self.has_key(actor.uid):
         self.add_actor(actor)
      else:
         self[actor.uid] = actor
