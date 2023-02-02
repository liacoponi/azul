import collections
import itertools
import random

factory = Factory()
bag = Bag()

global factory, bag

class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.victory_points = 0
        self.floor_tiles = [] 
        self.wall = Wall()
        self.pattern_lines = []
        for row in range(0, 5):
            self.pattern_lines.append([None for tile_spaces in range(0, row)])
        self.has_1 = 0

    def pick_tiles(display, color, pattern_line_row):
        picked_tiles = factory.pick(color, display)
        if self.pattern_line[pattern_line_row]: # validate pick, todo
            if ['1'] in picked_tiles:
                self.floor_tiles.append('1')
            self.pattern_line[pattern_line_row] += picked_tiles
        

    def turn_end(self):
        victory_points_before = self.victory_points
        # Add pattern line tiles to the wall
        for row_number, row in enumerate(self.floor_tiles):
            row_color = row[0]
            if None not in row:
                # row is complete, move tile and add points
                self.victory_points += self.Wall.add(row_color, row_number)
        
        # Reset floor tiles and pattern lines
        self.floor_tiles = []
        self.pattern_lines = []

        return victory_points_before - self.victory_points


class Bag:
    def __init__(self):
        self.tiles = []
        self.fill_bag()

    def fill_bag():
        self.tiles = [tile*20 for tile in ['bk', 'bl', 'red', 'orange', 'white']]

    def pick_from_bag(n):
        if n > len(self.tiles):
            # not sure if we should pick the tiles first, then shuffle. Don't care, cause it's for 1v1
            self.fill_bag()
        return [self.tiles.pop() for _ in range(n))

class Factory:
    def __init__(self):
        return True

    def pick(display_num, color):
        tiles_num = count(display_num, color)
        self.display[display_num] = [] 
        # picked from the center
        if display_num:
            self.display[0] = []
        return tiles_num, first_player

class Wall:
    def __init__(self):
	    self.wall = [None*5][None*5]]

    def add(self, tile_color, row_number):
        self.wall[row_number][0] # TODO
               

class Display:
    def __init__(self):
        return True

class PatternTiles:
    def __init__(self):
        return True
