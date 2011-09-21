#!/usr/bin/env python

import pygame, thing

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
PINK  = (255, 128, 128)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
LIGHTBLUE = (48, 48, 255)

# FONTS
fontsize = 16
marginwidth = 5
linespacing = 5
basicFont = pygame.font.SysFont('couriernew', fontsize)
line1 = basicFont.render('Catch the pigs using the arrow keys.', True, GREEN, BLACK)
line2 = basicFont.render("Press 'm' to toggle music.   ESC to quit.", True, GREEN, BLACK)
letterFont = pygame.font.SysFont('arial', 12)

scoreboard_header = basicFont.render("SCORES", True, GREEN, BLACK)
score_lines = []
actor_letters = {}
pig_numbers = {}

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
        


def render_world(window, world, redraw=False):
    global actor_letters
    tile_size = 16
    # Draw the terrain
    if redraw:
        for row, rownum in zip(world.terrain, range(len(world.terrain))):
            for tile, colnum in zip(world.terrain[rownum], range(len(world.terrain[rownum]))):
                if tile == 'X':
                    pygame.draw.rect(
                        window, GREEN, 
                        (colnum * tile_size, rownum * tile_size, tile_size, tile_size))
    # Erase all the actor's old stuff
    for actor in world.cast:
        if (actor.old_row == None) or (actor.old_col == None):
            continue
        old_tile_rect = pygame.Rect(actor.old_col * tile_size, actor.old_row * tile_size, tile_size, tile_size)
        pygame.draw.rect(window, BLACK, old_tile_rect)        

    # Draw the Actors
    for actor in world.cast:
        tile_rect = pygame.Rect(actor.col * tile_size, actor.row * tile_size, tile_size, tile_size)
        if type(actor) == thing.Actor:
            pygame.draw.rect(window, LIGHTBLUE, tile_rect)
            letter = actor.uid[0]
            if not actor_letters.has_key(letter):
                actor_letters[letter] = letterFont.render(letter, True, WHITE, LIGHTBLUE)
            letter_rect = actor_letters[letter].get_rect()
            letter_rect.centerx = tile_rect.centerx - 1
            letter_rect.top = tile_rect.top + 2
            window.blit(actor_letters[letter], letter_rect)
        elif type(actor) == thing.Pig:
            pygame.draw.rect(window, PINK, tile_rect)
            number = actor.value
            if not pig_numbers.has_key(number):
                pig_numbers[number] = letterFont.render(str(number), True, WHITE, PINK)
            number_rect = pig_numbers[number].get_rect()
            number_rect.centerx = tile_rect.centerx - 1
            number_rect.top = tile_rect.top + 2
            window.blit(pig_numbers[number], number_rect)
        
        
            
