import logging
import random

import definitions

logging.basicConfig(format='%(message)s', level=logging.INFO)


def main(no_of_players, no_of_games):
    players = [definitions.Player(i) for i in range(no_of_players)]
    game = definitions.Game(players)
    if no_of_games < 0:
        while True:
            try:
                play(game)
            except KeyboardInterrupt:
                return True
    else:
        for i in range(no_of_games):
            play(game)

def play_a_turn(game, player):
    logging.info(f'{player.id} plays:')
    # randomly pick for now, add AI/Player input here
    display, color, to_line = random.choice(game.get_valid_moves(player.id))
    game.transfer_tiles(player, display, color, to_line)


def play(game):
    """ Play a game of Azul """
    # reset bag and factory, pick first player, etc.
    game.new_game()
    # play rounds until a player completes a row
    while not game.is_last_round:
        # turn starts, reset players' boards
        game.round_reset()
        # pick first player
        player_id = game.first_player_id - 1
        # play players' turns until there are no tiles left
        while not game.is_last_turn:
            player_id = (player_id + 1) % game.player_no
            play_a_turn(game, game.players[player_id])

        # end players' turn
        logging.info('** Turn ends **')
        for player in game.players:
            player.turn_end()
            # end the game
            if player.has_finished_row:
                game.is_last_round = True
            else:
                game.is_last_turn = False

    # End of game scoring
    logging.info('** Game ends **')
    for player in game.players:
        player.score_final_vp()
    game.final_scores()
    game.games_counter += 1


if __name__ == '__main__':
    main(no_of_players=2, no_of_games=2)
