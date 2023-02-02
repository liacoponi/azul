from seven_wonders import definitions as sw
import csv
import random
import os


def main(no_of_players=4, card_file='cards.tsv', wonder_file='wonders.tsv'):
    wonders = load_wonders(wonder_file)
    deck = populate_decks(load_cards(card_file), no_of_players)
    while True:
        players = [sw.Player(str(player)) for player in range(no_of_players)]
        try:
            play(players, deck, wonders)
        except KeyboardInterrupt:
            pass


def play(players, original_deck, original_wonders):
    sw.discarded_cards = []
    deck = original_deck[:]
    wonders = original_wonders[:]
    print("\n** Wonders **")
    for i, p in enumerate(players):
        p.player_i = i
        random.shuffle(wonders)
        p.wonder = iter(wonders[random.randint(0, 1)])
        del wonders[0:2]
        if not isinstance(p.wonder.resources, str):
            p.resources += p.wonder.resources
        print("Player {}: {}".format(p.name, p.wonder.name))
        p.adjacent_players_i = ((p.player_i - 1) % len(players),
                              (p.player_i + 1) % len(players))
    for age, hand in enumerate(deck):
        print("\n** Beginning of age %s **" % str(age + 1))
        # create a deck for each player
        random.shuffle(hand)
        cards_per_deck = int(len(hand) / len(players))
        player_decks = [hand[cards_per_deck * i:cards_per_deck * (i + 1)] for i in range(0, len(players))]
        # Index used to track deck->player map. If it's 1, then p1 plays first, then p2 second, etc.
        deck_index = 0
        # until decks have one card left
        while len(player_decks[0]) > 1:
            # assign a deck to each player and play a card
            for p_i in range(len(players)):
                player = players[p_i]
                deck_i = (deck_index + p_i) % len(players)
                player.deck = player_decks[deck_i]
                player_decks[deck_i], players = player.play_a_turn(players, player_decks[deck_i])
            # shift the decks to the right if it's age 2
            if age == 1:
                deck_index += 1
            else:
                deck_index -= 1
            print()

        print('** Fighting begins **')
        for p in range(len(players) - 1):
            players[p].military_tokens, players[p + 1].military_tokens = resolve_fight(players[p], players[p + 1], age)
            # First and last players also fight
        players[0].military_tokens, players[-1].military_tokens = resolve_fight(players[0], players[-1], age)
        print()

    for p in players:
        print("Player %s:\n\tResources: %s\n\tSplit resources: %s" % (p.name, p.resources, p.split_resources))

    calculate_victory_points(players)


def calculate_victory_points(players):
    def calc_science_vp(player):
        def science_formula(resources):
            return (resources['&'] ** 2 + resources['#'] ** 2 + resources['@'] ** 2 +
            7 * min([resources['&'], resources['#'], resources['@']]))

        p_resources = player.resources
        if 'Scientists' in [c.name for c in player.played_cards]:
            resource_candidates = []
            for symbol in ['&', '#', '@']:
                tmp_resources = p_resources
                tmp_resources[symbol] += 1
                resource_candidates.append(science_formula(tmp_resources))
            return sorted(resource_candidates)[-1]
        return science_formula(p_resources)

    def calc_commerce_vp(player):
        vp = 0
        played_cards_names = [c.name for c in player.played_cards]
        if 'Haven' in played_cards_names:
            vp += sw.count_card_types('brown', [player])
        if 'Lighthouse' in played_cards_names:
            vp = sw.count_card_types('yellow', [player])
        if 'Haven' in played_cards_names:
            vp += sw.count_card_types('gray', [player]) * 2
        return vp

    def calc_guilds_vp(this_player, adjacent_players):
        vp = []
        played_cards_names = [c.name for c in this_player.played_cards]
        if 'Workers' in played_cards_names:
            vp.append(sw.count_card_types('brown', adjacent_players))
        if 'Craftsmen' in played_cards_names:
            vp.append(sw.count_card_types('gray', adjacent_players) * 2)
        if 'Traders' in played_cards_names:
            vp.append(sw.count_card_types('yellow', adjacent_players))
        if 'Philosophers' in played_cards_names:
            vp.append(sw.count_card_types('green', adjacent_players))
        if 'Spies' in played_cards_names:
            vp.append(sw.count_card_types('red', adjacent_players))
        if 'Magistrates' in played_cards_names:
            vp.append(sw.count_card_types('blue', adjacent_players))
        if 'Strategists' in played_cards_names:
            vp.append(sum([1 for player in adjacent_players for token in player.military_tokens if token == -1]))
        if 'Ship-owners' in played_cards_names:
            vp.append(sum([1 for card in this_player.played_cards if card.type in ['brown', 'gray', 'guild']]))
        if 'Builders' in played_cards_names:
            vp.append(sum([player.wonder.current_stage for player in players]))
        return vp

    all_victory_points = dict()
    print("\n** Victory Points **")
    # We do it in two loops to use copy_guild_cards, not very elegant, but works fine.
    for p in players:
        adjacent_players = [players[i] for i in p.adjacent_players_i]
        p.victory_points['Guilds']: sum(calc_guilds_vp(p, adjacent_players))

    for p in players:
        adjacent_players = [players[i] for i in p.adjacent_players_i]
        p.victory_points = {
            'Military': sum(p.military_tokens),
            'Treasury': p.resources['$'] // 3,
            'Wonder': p.resources['W'],
            'Blue cards': p.resources['V'],
            'Commerce': calc_commerce_vp(p),
            'Science': calc_science_vp(p),
        }
        if p.wonder.specials['copy_guild_card']:
            highest_vp_guilds = []
            for adj_p in adjacent_players:
                adj_adj_p = [players[i] for i in adj_p.adjacent_players_i]
                highest_vp_guilds += [vp for vp in calc_guilds_vp(adj_p, adj_adj_p)]
            p.victory_points['Copied Guild: '] = sorted(highest_vp_guilds)[-1] if highest_vp_guilds else 0
        p.victory_points['Total'] = sum(p.victory_points.values())
        formatted_points = ["\n{:>15}: {}".format(k, v) for k, v in p.victory_points.items()]
        print("\nPlayer %s:%s" % (p.name, ''.join(formatted_points)))
        all_victory_points[p.name] = p.victory_points['Total']

    print("\n**Ranking**",
          ''.join(["\n\tPlayer {}: {}".format(k, v) for k, v
                   in sorted(all_victory_points.items(), key=lambda item: item[1], reverse=True)]))


def resolve_fight(fighter_one, fighter_two, age):
    print("%s vs %s:" % (fighter_one.name, fighter_two.name), end=' ')
    if fighter_one.resources['X'] > fighter_two.resources['X']:
        # The formula gives 1, 3 and 5 victory points for age 1, 2, 3
        fighter_one.military_tokens.append(1 + age * 2)
        fighter_two.military_tokens.append(-1)
        print(fighter_one.name + " wins")
    elif fighter_one.resources['X'] < fighter_two.resources['X']:
        fighter_one.military_tokens.append(1 + age * 2)
        fighter_two.military_tokens.append(-1)
        print(fighter_two.name + " wins")
    else:
        print('draw!')
    return fighter_one.military_tokens, fighter_two.military_tokens


def load_cards(card_file='cards.tsv'):
    """Create a list of card object from a tsv file with card descriptions."""
    with open(os.path.join('data', card_file)) as card_file:
        card_reader = csv.reader(card_file, delimiter='\t')
        next(card_reader, None)
        return [sw.Card(line) for line in card_reader]


def populate_decks(card_list, no_of_players):
    """Returns a list of three shuffled decks"""
    decks = [[] for _ in range(3)]
    guild_cards = []
    for age in range(1, 4):
        for card in card_list:
            if card.age == age:
                if not card.cards_per_players:
                    # it's a guild card
                    guild_cards.append(card)
                    continue
                number_of_cards = card.cards_per_players[no_of_players - 1]
                for _ in range(0, number_of_cards):
                    decks[age - 1].append(card)
    # Add guild cards to age 3 deck
    random.shuffle(guild_cards)
    # According to Tofino
    decks[2] += guild_cards[0:no_of_players + 3]
    for deck in decks:
        random.shuffle(deck)
    return decks


def load_wonders(wonders_file):
    """Load list of wonders from a tsv file."""
    with open(os.path.join('data', wonders_file)) as w_file:
        wonder_reader = csv.reader(w_file, delimiter='\t')
        next(wonder_reader)
        wonders = {}
        for line in wonder_reader:
            if not line:
                continue
            try:
                name, cost, resources, stage, side = line
            except ValueError:
                raise ValueError('invalid line: ' + str(line))
            cost = sw.Resource(cost)
            name = name + '_' + side
            if resources.startswith('>'):
                resources = resources[1:]
            elif '/' not in resources:
                resources = sw.Resource(resources)
            if name not in wonders:
                wonders[name] = sw.Wonder(name, side, resources)
            else:
                wonders[name].stages.append((cost, resources))
    return [wonders[wonder] for wonder in wonders.keys()]


if __name__ == '__main__':
    main(3)
