import pygame, sys
from treasure import *

class Map(object):
   def __init__(self, p1, send, terrain):
      self.send    = send
      self.terrain = terrain
      self.cast    = Cast()
      self.p1      = p1
      self.cast.update(p1)
      self.dirty   = True  # Set to false whenever the graphics modules draws the map

   
   def move_player(self, direction):
      bound_row = len(self.terrain) - 1
      bound_col = len(self.terrain[0]) - 1
      newrow = self.p1.row
      newcol = self.p1.col
      if direction == 'up':
         newrow -= 1
         if newrow < 0:
            newrow = 0
      elif direction == 'down':
         newrow += 1
         if newrow > bound_row:
            newrow = bound_row
      elif direction == 'right':
         newcol += 1
         if newcol > bound_col:
            newcol = bound_col
      elif direction == 'left':
         newcol -= 1
         if newcol < 0:
            newcol = 0
      
      # You can't walk through solid objects!
      okay_to_move = True
      if self.terrain[newrow][newcol] == 'X':
         okay_to_move = False
      # You can't walk over other players!
      for player in self.cast.actors_of_type(Player):
         if (player.uid != self.p1.uid) and player.collide((newrow,newcol)):
            okay_to_move = False
      # Actually move, if we can.
      if okay_to_move:
         self.p1.set_location(newrow, newcol)
         self.send('move_actor')
         self.dirty = True
      else:
         self.p1.reset_move_timer()


   def update(self, delta):
      self.p1.update(delta)
      

   def remove_actor(self, actor):
      if type(actor) == Pig:
         user_events.post('sound', sound='oink')
      elif type(actor) == Player:
         user_events.post('sound', sound='byebye')
      self.cast.remove(actor)
      self.dirty = True
   
   def update_actor(self, actor):
      if (type(actor) == Player) and not self.cast.has_actor(actor):
         user_events.post('sound', sound='iamhere')
      self.cast.update(actor)
      self.dirty = True
