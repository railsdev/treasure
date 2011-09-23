#!/usr/bin/env python

import pygame
from treasure import *

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
high_score = None
player_letters = {}
pig_numbers = {}

def set_scoreboard(scoreboard):
    global score_lines
    global high_score
    score_lines = []
    for uid, score in scoreboard:
        score_lines.append(basicFont.render("%4d: %s" % (score, uid), True, GREEN, BLACK))
    if scoreboard.last_winner:
        high_score = basicFont.render("Last round's winner: %s with %d points." % (scoreboard.last_winner, scoreboard.last_high_score), True, GREEN, BLACK)

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
    if high_score:
        line_num += 1
        high_score_rect = high_score.get_rect()
        high_score_rect.left = window.get_rect().centerx + marginwidth
        high_score_rect.top = window.get_rect().top + line_num * (fontsize + linespacing)
        window.blit(high_score, high_score_rect)
        line_num += 1
        


def render_world(window, world, redraw=False):
    global player_letters
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
    for actor in (world.cast.actors_of_type(Player) + world.cast.actors_of_type(Pig)):
        if (actor.old_row == None) or (actor.old_col == None):
            row, col = actor.row, actor.col
        else:
            row, col = actor.old_row, actor.old_col
        tile_rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
        pygame.draw.rect(window, BLACK, tile_rect)        

    # Draw the pigs
    for pig in world.cast.actors_of_type(Pig):
        pig_rect = pygame.Rect(pig.col * tile_size, pig.row * tile_size, tile_size, tile_size)
        pygame.draw.rect(window, PINK, pig_rect)
        number = pig.value
        if not pig_numbers.has_key(number):
            pig_numbers[number] = letterFont.render(str(number), True, WHITE, PINK)
        number_rect = pig_numbers[number].get_rect()
        number_rect.centerx = pig_rect.centerx - 1
        number_rect.top = pig_rect.top + 2
        window.blit(pig_numbers[number], number_rect)
        
    # Draw the players
    for player in world.cast.actors_of_type(Player):
        player_rect = pygame.Rect(player.col * tile_size, player.row * tile_size, tile_size, tile_size)
        pygame.draw.rect(window, LIGHTBLUE, player_rect)
        letter = player.name[0]
        if not player_letters.has_key(letter):
            player_letters[letter] = letterFont.render(letter, True, WHITE, LIGHTBLUE)
        letter_rect = player_letters[letter].get_rect()
        letter_rect.centerx = player_rect.centerx - 1
        letter_rect.top = player_rect.top + 2
        window.blit(player_letters[letter], letter_rect)

        
            
