import logging
import random

COLORS = ['blue', 'orange', 'red', 'black', 'white']


class Bag:
    def __init__(self):
        self.tiles = []

    def refill_bag(self):
        logging.info("- Refill bag")
        self.tiles = [tile for tile in COLORS for _ in range(20)]
        random.shuffle(self.tiles)

    def pick_from_bag(self):
        if len(self.tiles) < 4:
            # TODO: should take then refill
            self.refill_bag()
        return [self.tiles.pop(0) for _ in range(4)]


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
        # picked from display, remove all tiles from display and add discarded tiles to the center
        else:
            self.displays[display_num] = []
            self.displays[0] += discarded_tiles
        return picked_tiles

    def get_valid_picks(self):
        valid_picks = []
        for i in range(len(self.displays)):
            for color in set(self.displays[i]):
                valid_picks.append((i, color))
        return valid_picks


class Wall:
    def __init__(self):
        # create the wall, upper means empty
        wall_space = [[tile.upper() for tile in COLORS]]
        for i in range(1, 5):
            rotated_list = [wall_space[i - 1][4]] + wall_space[i - 1][0:4]
            wall_space.append(rotated_list)
        self.wall_space = wall_space

    def add_tile(self, tile_color, line_num):
        logging.info(f'\tAdd {tile_color} to wall line {line_num}')
        wall_tile_index = self.wall_space[line_num].index(tile_color.upper())
        self.wall_space[line_num][wall_tile_index] = tile_color.lower()
        return True


class Game:
    def __init__(self, players):
        self.players = players
        self.player_no = len(players)
        self.factory = Factory(self.player_no)
        self.bag = Bag()
        self.first_player_id = 0
        self.games_counter = 0
        self.is_last_turn = False
        self.is_last_round = False

    def new_game(self):
        logging.info("\n** Game starts **")
        self.factory = Factory(self.player_no)
        self.bag.refill_bag()
        self.games_counter += 1
        self.pick_first_player()

    def pick_first_player(self):
        self.first_player_id = random.randint(0, self.player_no)

    def round_reset(self):
        # reset factory displays and center
        logging.info('\n** Round Setup Starts **')
        self.factory.displays[0] = ['1']
        for i in range(1, len(self.factory.displays)):
            self.factory.displays[i] = self.bag.pick_from_bag()
            logging.info(f'- Refill display {i}:  {self.factory.displays[i]}')
        # reset players' pattern tiles and floor
        for player in self.players:
            player.reset_lines()
        logging.info('\n** Round Play Starts **')

    def get_valid_moves(self, player_id):
        player = self.players[player_id]
        valid_picks = self.factory.get_valid_picks()
        # last move
        if len(valid_picks) == 1:
            self.is_last_turn = True
        valid_line_colors = player.get_valid_line_colors()
        valid_moves = []
        for valid_pick in valid_picks:
            display, color = valid_pick
            if color != '1':
                valid_moves_tuples = tuple((display, color, line) for line in valid_line_colors[color])
                for valid_tuple in valid_moves_tuples:
                    valid_moves.append(valid_tuple)
            valid_moves.append((display, color, 'floor'))
        return valid_moves

    def transfer_tiles(self, player, display_num, color, to_line):
        selected_tiles = self.factory.pick_from_display(display_num, color)
        if ['1'] in selected_tiles:
            self.first_player_id = player.id
        # add tiles to player pattern and floor lines
        player.place_tiles(selected_tiles, to_line)
        logging.info(f'\t{color}: {display_num} -> {to_line}')


class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.victory_points = 0
        self.wall = Wall()
        self.pattern_lines = []
        self.victory_points_last_turn = 0
        self.has_finished_row = 0
        self.floor = []

    def reset_lines(self):
        logging.info(f'- Player {self.id} resets their lines')
        self.pattern_lines = [[None for _ in range(size)] for size in range(1, 6)]

    def reset_board(self):
        self.reset_lines()
        self.wall = Wall()

    def place_tiles(self, tiles, to_line):
        # '1' is not passed as a tile
        # place_tiles is not called for floor
        if '1' in tiles:
            self.floor.append('1')
            tiles.remove('1')
            # only 1st player tile is picked
            if not tiles:
                return True
        if to_line != 'floor':
            target_line = self.pattern_lines[to_line]
            for i, tile_space in enumerate(target_line):
                # tile space is empty, put the tile
                if tile_space is None:
                    try:
                        target_line[i] = tiles.pop(0)
                    # no more tiles to add
                    except IndexError:
                        break

        # add leftover tiles to the floor
        self.floor += tiles

    def turn_end(self):
        # Add pattern-line tiles to the wall
        for line_number, line in enumerate(self.pattern_lines):
            if all(line):
                # pattern line is complete, move tile and add points
                self.victory_points += self.wall.add_tile(line[0], line_number)
                # completed row in wall, end game
                if all(self.wall.wall_space[line_number]):
                    self.has_finished_row = True

        floor_scores = {0: 0, 1: 1, 2: 2, 3: 4, 4: 6, 5: 8, 6: 11, 7: 14}
        floor_malus = floor_scores[min(len(self.floor), 7)]
        self.victory_points -= floor_malus
        self.floor = []
        logging.info(f'\t-{floor_malus} VP: Floor tiles')

    def get_valid_line_colors(self):
        """return a list containing a list of valid/acceptable color tile for each line"""
        # defines in which lines you can put each color
        valid_color_lines = {color: [] for color in COLORS}
        for color in COLORS:
            for i, line in enumerate(self.pattern_lines):
                if color in self.wall.wall_space[i]:
                    continue
                line_is_empty = not any(line)
                # e.g. True:  W -> ['W', None]; W -> [None, None]
                # e.g. False: W -> ['Bl', None]
                if color in line or line_is_empty:
                    valid_color_lines[color].append(i)
        return valid_color_lines

    @staticmethod
    def score_final_vp():
        # ToDo: finis method and add score breakdown
        return 10
