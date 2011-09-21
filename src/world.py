import pygame, sys, thing

class Map(object):
   def __init__(self, p1, send, terrain):
      self.send    = send
      self.terrain = terrain
      self.cast    = thing.Cast()
      self.p1      = p1
      self.cast.add_actor(p1)
      self.dirty   = True  # Set to false whenever the graphics modules draws the map

   
   def move_player(self, direction):
      bound_row = len(self.terrain) - 1
      bound_col = len(self.terrain[0]) - 1
      newrow = self.p1.row
      newcol = self.p1.col
      if direction == pygame.K_UP:
         newrow -= 1
         if newrow < 0:
            newrow = 0
      elif direction == pygame.K_DOWN:
         newrow += 1
         if newrow > bound_row:
            newrow = bound_row
      elif direction == pygame.K_RIGHT:
         newcol += 1
         if newcol > bound_col:
            newcol = bound_col
      elif direction == pygame.K_LEFT:
         newcol -= 1
         if newcol < 0:
            newcol = 0
      
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
         self.p1.set_location(newrow, newcol)
         self.send('move_actor')
         self.dirty = True
      else:
         self.p1.reset_move_timer()


   def update(self, delta):
      self.p1.update(delta)
      
   def add_actor(self, actor):
      if type(actor) == thing.Actor:
         pygame.event.post(pygame.event.Event(pygame.USEREVENT, subtype='sound', sound='iamhere'))
      self.cast.add_actor(actor)
      self.dirty = True

   
   def rm_actor(self, actor):
      if type(actor) == thing.Pig:
         pygame.event.post(pygame.event.Event(pygame.USEREVENT, subtype='sound', sound='oink'))
      elif type(actor) == thing.Actor:
         pygame.event.post(pygame.event.Event(pygame.USEREVENT, subtype='sound', sound='byebye'))
      self.cast.rm_actor(actor)
      self.dirty = True
   
   def update_actor(self, actor):
      if self.cast.has_actor(actor):
         self.cast.update_actor(actor)
         self.dirty = True
      else:
         self.add_actor(actor)
