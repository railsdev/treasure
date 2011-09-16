#!/usr/bin/env python

import pygame, thing

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
PINK  = (255, 128, 128)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

# FONTS
basicFont = pygame.font.SysFont('couriernew', 16)
text = basicFont.render('Catch the pigs.  Arrow keys.  ESC to quit.', True, GREEN, BLACK)

def render_text(window):
    textRect = text.get_rect()
    textRect.left = window.get_rect().centerx + 5
    textRect.top = window.get_rect().top
    window.blit(text, textRect)


def render_world(window, world):
    tile_size = 16
    # Draw the terrain
    for row, rownum in zip(world.terrain, range(len(world.terrain))):
        for tile, colnum in zip(world.terrain[rownum], range(len(world.terrain[rownum]))):
            if tile == 'X':
                pygame.draw.rect(
                    window, GREEN, 
                    (colnum * tile_size, rownum * tile_size, tile_size, tile_size))
    # Draw the Actors
    for actor in world.cast:
        if type(actor) == thing.Actor:
            color = BLUE
        else:
            color = PINK
        pygame.draw.rect(
            window, color, 
            (actor.col * tile_size, actor.row * tile_size, tile_size, tile_size))
            
