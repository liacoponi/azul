import random


class Bag:
    def __init__(self):
        self.tiles = []

    def refill_bag(self):
        # TODO: make a tile object
        self.tiles = [tile * 20 for tile in ['bk', 'bl', 'red', 'orange', 'white']]
        random.shuffle(self.tiles)

    def pick_from_bag(self):
        if len(self.tiles) < 4:
            # TODO: should take then refill
            self.refill_bag()
        return [self.tiles.pop() for _ in range(4)]


class Factory:
    def __init__(self, no_of_players):
        # 2 player -> 5 displays, 3 -> 7, 4 -> 9
        self.no_of_displays = no_of_players * 2 + 1
        self.displays = [None for _ in range(self.no_of_displays)]
        self.center = []
        self.center = ['1']

    def pick_from_display(self, display_num, color):
        tiles_num = self.count(display_num, color)
        self.display[display_num] = []
        # picked from the center
        if display_num:
            self.display[0] = []
        return tiles_num


class Wall:
    def __init__(self):
        self.wall = [['' * 5]['' * 5]]

    def add_tile(self, tile_color, row_number):
        self.wall[row_number][0] = 0  # TODO


class PatternLine:
    def __init__(self, size):
        self.line_color = None
        self.tiles_left = size

    def fill_line(self, color, tiles_to_add):
        if not self.tiles:
            return tiles_to_add
        # different color, return all tiles
        if self.line_color and self.line_color != color:
            return tiles_to_add
        else:
            tile_diff = tiles_to_add - tiles_to_add
            self.tiles_left = max(0, tile_diff)
            # return tiles to drop on floor tile
            return min(tile_diff, 0)


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

    def pick_first_player(self, number_of_players):
        self.first_player_id = random.randint(0, number_of_players)

    def turn_reset(self):
        # reset factory displays and center
        for i in range(self.factory.displays):
            self.factory.displays[i] = self.bag.pick_from_bag(4)
        self.factory.center = ['1']
        # reset players' pattern tiles and floor
        for player in self.players:
            player.reset_lines()

    def is_last_turn(self):
        if not self.factory.center and not any(self.factory.displays):
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
        self.pattern_lines = [PatternLine(size) for size in range(5)]
        self.floor_tiles = []

    def reset_board(self):
        self.reset_lines()
        self.wall.clear_wall()

    def pick_tiles(self, display, color, pattern_line_row):
        picked_tiles = factory.pick(color, display)
        # ['white', 'white', '1']
        if ['1'] in picked_tiles:
            self.floor_tiles.append('1')
            self.game.is_first = self.player_id
            picked_tiles.remove('1')

        n_of_discarded_tiles = self.pattern_lines[pattern_line_row].fill_line(color, picked_tiles)
        self.floor_tiles.append(color * n_of_discarded_tiles)

    def turn_end(self):
        victory_points_before = self.victory_points
        # Add pattern line tiles to the wall
        for row_number, row in enumerate(self.floor_tiles):
            row_color = row[0]
            if None not in row:
                # pattern line is complete, move tile and add points
                self.victory_points += self.wall.add(row_color, row_number)
                # completed row in wall, end game
                if None not in self.wall.row[row_number]:
                    self.has_finished_row = True

        self.victory_points_last_turn = victory_points_before - self.victory_points

    def score_final_vp(self):
        # ToDo: finis method and add score breakdown
        return 10
