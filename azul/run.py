import csv
import random
import os
import definitions


def main(no_of_players):
    players = [definitions.Player() for p in no_of_players]
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
    game.set_up()
    print("\n** Game Starts **")
    # turn starts, reset player boards
    game.turn_reset()
    # reset pattern_lines, just in case



if __name__ == '__main__':
    main(no_of_players=2)
