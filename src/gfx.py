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

scoreboard_header = basicFont.render("SCORES", True, GREEN, BLACK)
score_lines = []

def set_scoreboard(scoreboard):
    global score_lines
    score_lines = []
    for uid, score in scoreboard:
        score_lines.append(basicFont.render("%4d: %s" % (score, uid), True, GREEN, BLACK))

def render_text(window):
    line1Rect = line1.get_rect()
    line1Rect.left = window.get_rect().centerx + marginwidth
    line1Rect.top = window.get_rect().top
    window.blit(line1, line1Rect)
    line2Rect = line2.get_rect()
    line2Rect.left = window.get_rect().centerx + marginwidth
    line2Rect.top = window.get_rect().top + (fontsize + linespacing)
    window.blit(line2, line2Rect)
    
    scoreboard_headerRect = scoreboard_header.get_rect()
    scoreboard_headerRect.left = window.get_rect().centerx + marginwidth
    scoreboard_headerRect.top = window.get_rect().top + 3 * (fontsize + linespacing)
    window.blit(scoreboard_header, scoreboard_headerRect)
    
    line_num = 4
    for line in score_lines:
        lineRect = line.get_rect()
        lineRect.left = window.get_rect().centerx + marginwidth
        lineRect.top = window.get_rect().top + line_num * (fontsize + linespacing)
        window.blit(line, lineRect)
        line_num += 1
        


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
            
