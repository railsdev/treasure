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
fontsize = 16
marginwidth = 5
linespacing = 5
basicFont = pygame.font.SysFont('couriernew', fontsize)
line1 = basicFont.render('Catch the pigs using the arrow keys.', True, GREEN, BLACK)
line2 = basicFont.render("Press 'm' to toggle music.   ESC to quit.", True, GREEN, BLACK)

def render_text(window):
    line1Rect = line1.get_rect()
    line1Rect.left = window.get_rect().centerx + marginwidth
    line1Rect.top = window.get_rect().top
    window.blit(line1, line1Rect)
    line2Rect = line2.get_rect()
    line2Rect.left = window.get_rect().centerx + marginwidth
    line2Rect.top = window.get_rect().top + (fontsize + linespacing)
    window.blit(line2, line2Rect)


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
            
