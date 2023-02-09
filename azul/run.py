import logging
import random

import definitions

logging.basicConfig(format='%(message)s', level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


def main(no_of_players):
    players = [definitions.Player(i) for i in range(no_of_players)]
    game = definitions.Game(players)
    # continuously play new games until KeyboardInterrupt
    while True:
        try:
            play(game)
        except KeyboardInterrupt:
            return True


def play_a_turn(game, player):
    logging.info(f'{player.id} plays:')
    valid_picks = game.factory.get_valid_picks()
    # last move
    if len(valid_picks) == 1:
        game.is_last_turn = True
    valid_moves = []  # TODO
    # randomly pick for now, add AI/Player input here
    display, color = random.choice(valid_moves)
    pattern_line_row = random.randint(0, 4)
    logging.info(f'\tdisplay: {display}\n\tcolor: {color}\n\tto line: {pattern_line_row}')
    game.transfer_tiles(player.id, display, color, pattern_line_row)


def play(game):
    """ Play a game of Azul """
    # reset bag and factory, pick first player, etc.
    game.new_game()
    logging.info("\n** Game Starts **")
    # play rounds until a player completes a row
    while not game.is_last_round:
        # turn starts, reset players' boards
        game.turn_reset()
        # pick first player
        player_id = game.first_player_id - 1
        logging.info(f'{player_id + 1} starts a new round')
        # play players' turns until there are no tiles left
        while not game.is_last_turn:
            player_id = (player_id + 1) % game.player_no
            play_a_turn(game, game.players[player_id])

        # end player turn and possibly the game
        for player in game.players:
            player.turn_end()
            if player.has_finished_row:
                game.is_last_round = True

    # End of game scoring
    for player in game.players:
        player.score_final_vp()


if __name__ == '__main__':
    main(no_of_players=2)
