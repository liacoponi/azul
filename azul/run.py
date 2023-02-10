import logging

import definitions

logging.basicConfig(format='%(message)s', level=logging.INFO)


def main(no_of_players, no_of_games):
    players = [definitions.Player(i) for i in range(no_of_players)]
    game = definitions.Game(players)
    if no_of_games < 0:
        while True:
            try:
                game.play_a_game()
            except KeyboardInterrupt:
                return True
    else:
        for i in range(no_of_games):
            game.play_a_game()


if __name__ == '__main__':
    main(no_of_players=2, no_of_games=2)
