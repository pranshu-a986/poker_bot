import json
import sys
import itertools
from collections import Counter

RANKS = "23456789TJQKA"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}

def parse_card(card):
    return RANK_VALUE[card[0]], card[1]

def check_straight(vals):
    vals = sorted(vals)
    if vals == [2, 3, 14]:
        return True, 3
    if vals[0]+1 == vals[1] and vals[1]+1 == vals[2]:
        return True, vals[2]
    return False, 0

def hand_score(cards):
    vals, suits = [], []
    for c in cards:
        v, s = parse_card(c)
        vals.append(v)
        suits.append(s)

    counts = Counter(vals)
    count_vals = sorted(counts.values(), reverse=True)
    flush = len(set(suits)) == 1
    straight, high = check_straight(vals)

    if flush and straight:
        return (5, high)
    if count_vals[0] == 3:
        return (4, max(vals))
    if straight:
        return (3, high)
    if flush:
        return (2, sorted(vals, reverse=True))
    if count_vals[0] == 2:
        pair = max(v for v in counts if counts[v] == 2)
        kicker = max(v for v in counts if counts[v] == 1)
        return (1, pair, kicker)
    return (0, sorted(vals, reverse=True))

def calculate_equity(hole, table):
    deck = [r+s for r in RANKS for s in "CDHS"]
    for c in hole:
        deck.remove(c)
    deck.remove(table)

    my_hand = hand_score(hole + [table])
    wins = ties = total = 0

    for opp in itertools.combinations(deck, 2):
        opp_hand = hand_score(list(opp) + [table])
        total += 1
        if my_hand > opp_hand:
            wins += 1
        elif my_hand == opp_hand:
            ties += 1

    return (wins + 0.5 * ties) / total

def decide_action(state):
    hole = state["your_hole"]
    table = state["table_card"]
    equity = calculate_equity(hole, table)

    if equity < 0.25:
        return "FOLD"
    elif equity >= 0.50:
        return "RAISE"
    else:
        return "CALL"

def main():
    raw = sys.stdin.read().strip()
    state = json.loads(raw) if raw else {}
    action = decide_action(state)
    sys.stdout.write(json.dumps({"action": action}))

if __name__ == "__main__":
    main()
