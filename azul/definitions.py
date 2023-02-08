import random

tile_colors = ['or', 'rd', 'bk', 'wh', 'bl']


class Bag:
    def __init__(self):
        self.tiles = []

    def refill_bag(self):
        # TODO: make a tile object
        self.tiles = [tile * 20 for tile in tile_colors]
        random.shuffle(self.tiles)

    def pick_from_bag(self):
        if len(self.tiles) < 4:
            # TODO: should take then refill
            self.refill_bag()
        return [self.tiles.pop() for _ in range(4)]


class Factory:
    def __init__(self, no_of_players):
        # 2 player -> 5 displays, 3 -> 7, 4 -> 9
        # formula is x * 2 + 1
        # and adds another + 1 for the center, which is display[0]
        self.no_of_displays = no_of_players * 2 + 2
        self.displays = [None for _ in range(self.no_of_displays)]

    def pick_from_display(self, display_num, color):
        picked_tiles = [tile for tile in self.displays[display_num] if color == tile]
        discarded_tiles = [tile for tile in self.displays[display_num] if color != tile]
        # picked from the center, just remove tiles from the center
        if not display_num:
            self.displays[0] = [tile for tile in self.displays[0] if color != tile]
        # picked from display, add discarded tiles to the center
        else:
            self.displays[0] += discarded_tiles
        return picked_tiles


class Wall:
    def __init__(self):
        # rotate the list, then revert it to get the 5X5 wall
        w = tile_colors
        wall = []
        for _ in range(5):
            wall.append(w[:])
            wall.append(w.pop(0))
        self.wall = w.reverse()

    def add_tile(self, tile_color, row_number):
        self.wall[row_number][0] = 0  # TODO


class Game:
    def __init__(self, players):
        self.players = players
        self.player_no = len(players)
        self.factory = Factory(self.player_no)
        self.bag = Bag()
        self.first_player_id = 0
        self.games_counter = 0
        self.is_last_round = 0

    def new_game(self):
        self.factory = Factory(self.player_no)
        self.bag.refill_bag()
        self.games_counter += 1
        self.pick_first_player()

    def pick_first_player(self):
        self.first_player_id = random.randint(0, self.player_no)

    def turn_reset(self):
        # reset factory displays and center
        for i in range(len(self.factory.displays)):
            self.factory.displays[i] = self.bag.pick_from_bag()
        self.factory.center = ['1']
        # reset players' pattern tiles and floor
        for player in self.players:
            player.reset_lines()

    def transfer_tiles(self, player_id, display_num, color, row):
        selected_tiles = self.factory.pick_from_display(display_num, color)
        if ['1'] in selected_tiles:
            self.is_first = player_id
            selected_tiles.remove('1')
        # add tiles to player pattern and floor lines
        self.players[player_id].place_tiles(tiles=selected_tiles, pattern_line=row, picked_1=True)

    def is_last_turn(self):
        if not self.factory.displays[0] and not any(self.factory.displays):
            return True


class Player:
    def __init__(self, player_id):
        self.name = player_id
        self.victory_points = 0
        self.floor_tiles = []
        self.wall = Wall()
        self.pattern_lines = []
        self.victory_points_last_turn = 0
        self.has_finished_row = 0

    def reset_lines(self):
        # todo: fix this
        self.pattern_lines = [size for size in range(5)]
        self.floor_tiles = []

    def reset_board(self):
        self.reset_lines()
        self.wall = Wall()

    def place_tiles(self, tiles, pattern_line_num, picked_1):
        tile_color = tiles[0]
        line = self.pattern_lines[pattern_line_num]
        if picked_1:
            self.floor_tiles.append('1')
        # color not in the wall and line has no another color than tile_color
        if tile_color not in self.wall and (tile_color in line or not any(tiles)):
            for i, tile_space in enumerate(tiles):
                # tile space is empty
                if not tile_space:
                    try:
                        tiles[i] = tiles.pop(0)
                    # no more tiles to add
                    except IndexError:
                        break

        # add leftover tiles to the floor
        self.floor_tiles += tiles

    def turn_end(self):
        victory_points_before = self.victory_points
        # Add pattern line tiles to the wall
        for row_number, row in enumerate(self.floor_tiles):
            row_color = row[0]
            if None not in row:
                # pattern line is complete, move tile and add points
                self.victory_points += self.wall.add(row_color, row_number)
                # completed row in wall, end game
                if all(self.wall[row_number]):
                    self.has_finished_row = True

        self.victory_points_last_turn = victory_points_before - self.victory_points

    def score_final_vp(self):
        # ToDo: finis method and add score breakdown
        return 10
