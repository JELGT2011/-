from __future__ import division
from __future__ import print_function

import random
from collections import defaultdict, Counter
from itertools import combinations
from subprocess import call

from deuces import Card
from deuces.deck import Deck
from deuces.evaluator import Evaluator

evaluator = Evaluator()


# class Outcome:
#     def __init__(self):
#         self.occurrences = 0
#         self.probability = None
#         self.relations = {
#             'wins_to': list(),
#             'loses_to': list(),
#             'ties_to': list(),
#         }
#
#     def get_most_likely(self):
#         return
#
#
# class ResultSet:
#     def __init__(self):
#         self.outcomes = defaultdict(Outcome)
#
#     def incorporate(self, other):
#         self_weight = self.size / other.size
#         self.size += other.size
#         self.wins_to
#
#     def outcomes_by_rank(self):
#         pass


def draw_count(deck, count):
    copy = [card for card in deck]
    cards = [copy.pop() for _ in xrange(count)]
    return cards, copy


def draw_index(deck, *index):
    index = reversed(sorted(index))
    copy = [card for card in deck]
    cards = [copy.pop(i) for i in index]
    return cards, copy


def draw_combinations(deck, count):
    deck = set(deck)
    combos = combinations(deck, count)
    result = list()
    for combo in combos:
        d = deck - {c for c in combo}
        result.append((d, combo))
    return result


# def result_given_player(deck, player_hand):
#     boards = [list(perm) for perm in permutations(deck, 5)]
#     result = ResultSet()
#     for board in boards:
#         result.incorporate(result_given_player_and_board(deck, player_hand, board))
#
#     return result
#
#
# def result_given_player_and_board(deck, player_hand, board):
#     player_score = evaluator.evaluate(board, player_hand)
#     player_class = evaluator.get_rank_class(player_score)
#     player_class_string = evaluator.class_to_string(player_class)
#     adversary_hands = [list(perm) for perm in permutations(deck, 2)]
#     result = ResultSet()
#     for adversary_hand in adversary_hands:
#         adversary_score = evaluator.evaluate(board, adversary_hand)
#         adversary_class = evaluator.get_rank_class(adversary_score)
#         adversary_class_string = evaluator.class_to_string(adversary_class)
#         result.outcomes[adversary_class_string].occurrences += 1
#         if player_class < adversary_class:
#             result.outcomes[adversary_class_string].relations['loses_to'].append(adversary_hand)
#         elif adversary_class < player_class:
#             result.wins_to.append(adversary_hand)
#         else:
#             result.ties_to.append(adversary_hand)
#         result.outcomes.append(outcome)
#
#     return result
#
#
# def result_given_player_and_adversary(deck, player_hand, adversary_hand):
#     boards = [list(perm) for perm in permutations(deck, 5)]
#     result = ResultSet()
#     def iterate_boards():
#         pass
#     for board in boards:
#         player_score = evaluator.evaluate(board, player_hand)
#         player_class = evaluator.get_rank_class(player_score)
#         adversary_score = evaluator.evaluate(board, adversary_hand)
#         adversary_class = evaluator.get_rank_class(adversary_score)
#         if player_class < adversary_class:
#             result.loses_to.append(adversary_hand)
#         elif adversary_class < player_class:
#             result.wins_to.append(adversary_hand)
#         else:
#             result.ties_to.append(adversary_hand)
#
#     return result

def cards_to_str(cards):
    return {Card.int_to_str(card) for card in cards}


def cards_str_to_value(cards):
    return {card[0] for card in cards}


def cards_str_to_suit(cards):
    return {card[1] for card in cards}


def card_value_match(hand, board):
    return bool(cards_str_to_value(hand) & cards_str_to_value(board))


def card_suit_match(hand, board):
    return bool(cards_str_to_suit(hand) & cards_str_to_suit(board))


# def card_straight_match(hand, board):
#     hand_values = cards_str_to_value(hand)
#     board_values = cards_str_to_value(board)
#     Card.STR_RANKS
#     return any((hand_value + 1 in board_values or hand_value - 1 in  for hand_value in hand_values))


CLASS_STRING_TO_VALIDATION_FUNC = {
    'Straight Flush': lambda hand, board: True,  # for now, assume we use the hand (these values will be off)
    'Four of a Kind': card_value_match,
    'Full House': card_value_match,
    'Flush': card_suit_match,
    'Straight': lambda hand, board: True,  # for now, assume we use the hand (these values will be off)
    'Three of a Kind': card_value_match,
    'Two Pair': card_value_match,  # TODO: account for pocket pairs
    'Pair': card_value_match,
    'High Card': lambda hand, board: False,  # never count high card
}


def post_turn(players):
    print('Post Turn')

    deck = Deck()
    player_hand, remaining_post_players = draw_count(deck.cards, 2)
    adversary_hands = list()
    for i in range(players):
        adversary_hand, remaining_post_players = draw_count(remaining_post_players, 2)
        adversary_hands.append(adversary_hand)
    player_hand_str = cards_to_str(player_hand)
    flop_and_turn, remaining_post_board = draw_count(remaining_post_players, 4)

    print('Flop and Turn')
    Card.print_pretty_cards(flop_and_turn)
    print()

    print('Player hand')
    Card.print_pretty_cards(player_hand)
    print()

    print('Number of adversaries: {}'.format(players))
    print()

    raw_input('Press enter to continue...')

    outcome_counts_by_string = defaultdict(int)
    draw_combos = draw_combinations(remaining_post_board, 1)
    total = len(draw_combos)
    for remaining, river in draw_combos:
        board = flop_and_turn + list(river)
        player_score = evaluator.evaluate(board, player_hand)
        player_class = evaluator.get_rank_class(player_score)
        player_class_string = evaluator.class_to_string(player_class)
        validation_func = CLASS_STRING_TO_VALIDATION_FUNC[player_class_string]
        if not validation_func(player_hand_str, cards_to_str(board)):
            continue
        outcome_counts_by_string[player_class_string] += 1

    outcome_percentages_by_string = dict()
    for outcome, count in outcome_counts_by_string.iteritems():
        outcome_percentages_by_string[outcome] = (count / total) * 100
    outcome_percentages_by_string = Counter(outcome_percentages_by_string)

    print('Adversary hands')
    for adversary_hand in adversary_hands:
        Card.print_pretty_cards(adversary_hand)
    print()

    print('Outcomes')

    outcomes_limit = 10
    outcomes = outcome_percentages_by_string.most_common(outcomes_limit)
    for outcome, percentage in outcomes:
        print('{} ({}% percentage)'.format(outcome, percentage))

    raw_input('Press enter to continue...')

    call('clear', shell=True)


def post_flop(players):
    print('Post Flop')

    deck = Deck()
    player_hand, remaining_post_players = draw_count(deck.cards, 2)
    adversary_hands = list()
    for i in range(players):
        adversary_hand, remaining_post_players = draw_count(remaining_post_players, 2)
        adversary_hands.append(adversary_hand)
    player_hand_str = cards_to_str(player_hand)
    flop, remaining_post_board = draw_count(remaining_post_players, 3)

    print('Flop')
    Card.print_pretty_cards(flop)
    print()

    print('Player hand')
    Card.print_pretty_cards(player_hand)
    print()

    print('Number of adversaries: {}'.format(players))
    print()

    raw_input('Press enter to continue...')

    outcome_counts_by_string = defaultdict(int)
    draw_combos = draw_combinations(remaining_post_board, 2)
    total = len(draw_combos)
    for remaining, (turn, river) in draw_combos:
        board = flop + [turn, river]
        player_score = evaluator.evaluate(board, player_hand)
        player_class = evaluator.get_rank_class(player_score)
        player_class_string = evaluator.class_to_string(player_class)
        validation_func = CLASS_STRING_TO_VALIDATION_FUNC[player_class_string]
        if not validation_func(player_hand_str, cards_to_str(board)):
            continue
        outcome_counts_by_string[player_class_string] += 1

    outcome_percentages_by_string = dict()
    for outcome, count in outcome_counts_by_string.iteritems():
        outcome_percentages_by_string[outcome] = (count / total) * 100
    outcome_percentages_by_string = Counter(outcome_percentages_by_string)

    print('Adversary hands')
    for adversary_hand in adversary_hands:
        Card.print_pretty_cards(adversary_hand)
    print()

    print('Outcomes')

    outcomes_limit = 10
    outcomes = outcome_percentages_by_string.most_common(outcomes_limit)
    for outcome, percentage in outcomes:
        print('{} ({}% percentage)'.format(outcome, percentage))

    raw_input('Press enter to continue...')

    call('clear', shell=True)

#
# def pre_flop():
#     deck = Deck()
#     player_hand, remaining_post_player = draw_count(deck, 2)
#
#     result = ResultSet()
#     for idxs in [list(idxs) for idxs in permutations(range(len(remaining_post_player)), 5)]:
#         board, remaining_post_board = draw_index(remaining_post_player, idxs)
#         result.incorporate(result_given_player_and_board())
#         player_score = evaluator.evaluate(board, player_hand)
#         player_class = evaluator.get_rank_class(player_score)
#         key = evaluator.class_to_string(player_class)
#         for idxs in [list(perm) for perm in permutations(range(len(remaining_post_board)), 2)]:
#             adversary_hand, remaining = draw_index(remaining_post_board, idxs)
#
#         out = None
#         outs[key].append(out)
#         win_percentage = len(lose_to) / len(adversary_hands)
#         answer = FixedOption.YES if win_percentage >= 0.5 else FixedOption.NO
#
#     print('Player hand')
#     Card.print_pretty_cards(player_hand)
#     print()
#
#     print('Options: {}'.format(FixedOption.to_input()))
#     choice = FixedOption.from_input(raw_input('Choice: '))
#     correct = choice == answer
#     print('Win Percentage: {0:.2f}%'.format(win_percentage * 100))
#     print('Loses To:')
#
#     print('Correct' if correct else 'Incorrect')
#     raw_input('Press enter to continue...')
#     call('clear', shell=True)
#
#
# def post_river():
#     deck = Deck()
#     player_hand, remaining_post_player = draw_count(deck, 2)
#     board, remaining_post_board = draw_count(remaining_post_player, 5)
#     result = result_given_player_and_board(remaining_post_board, player_hand, board)
#     win_percentage = len(result.wins_to) / len(result.size)
#     answer = FixedOption.YES if win_percentage >= 0.5 else FixedOption.NO
#
#     print('Player hand')
#     Card.print_pretty_cards(player_hand)
#     print()
#
#     print('Board')
#     Card.print_pretty_cards(board)
#     print()
#
#     print('Options: {}'.format(FixedOption.to_input()))
#     choice = FixedOption.from_input(raw_input('Choice: '))
#     correct = choice == answer
#     print('Win Percentage: {0:.2f}%'.format(win_percentage * 100))
#
#     print('Correct' if correct else 'Incorrect')
#     raw_input('Press enter to continue...')
#     call('clear', shell=True)


if __name__ == '__main__':
    while True:
        players = random.randint(1, 5)
        if random.random() > 0.5:
            post_flop(players)
        else:
            post_turn(players)
