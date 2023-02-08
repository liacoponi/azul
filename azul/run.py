import random

import definitions


def main(no_of_players):
    players = [definitions.Player(i) for i in range(no_of_players)]
    game = definitions.Game(players)
    # continuously play new games until KeyboardInterrupt
    while True:
        try:
            play(game)
        except KeyboardInterrupt:
            return True


def play(game):
    """ Play a game of Azul """
    # reset bag and factory, pick first player, etc.
    game.new_game()
    print("\n** Game Starts **")
    while not game.is_last_round:
        # turn starts, reset players' boards
        game.turn_reset()
        player_turn_id = game.first_player_id - 1

        # each player plays a turn until there are no tiles left
        while not game.is_last_turn():
            player_turn_id = (player_turn_id + 1) % game.player_no
            print("Player's turn: " + str(player_turn_id))
            chosen_display = random.randint(-1, 5)
            chosen_color = random.choice(definitions.tile_colors)
            chosen_pattern_line_row = random.randint(0, 5)
            game.players[player_turn_id].pick_tiles(chosen_display, chosen_color, chosen_pattern_line_row)

        for player in game.players:
            player.turn_end()
            if player.has_finished_row:
                game.is_last_round = True

    # End of game scoring
    for player in game.players:
        player.score_final_vp()


if __name__ == '__main__':
    main(no_of_players=2)
