import json
import sys
import itertools
from collections import Counter

RANKS = "23456789TJQKA"
SUITS = "CDHS"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}

def parse_card(card):
    return RANK_VALUE[card[0]], card[1]

def check_straight(vals):
    vals = sorted(vals)
    if vals == [2, 3, 14]:
        return True, 3
    if vals[0] + 1 == vals[1] and vals[1] + 1 == vals[2]:
        return True, vals[2]
    return False, 0

def hand_rank(cards):
    values, suits = [], []
    for c in cards:
        v, s = parse_card(c)
        values.append(v)
        suits.append(s)

    counts = Counter(values)
    count_vals = sorted(counts.values(), reverse=True)
    flush = len(set(suits)) == 1
    straight, high = check_straight(values)

    if flush and straight:
        return (5, high)
    if count_vals[0] == 3:
        return (4, max(values))
    if straight:
        return (3, high)
    if flush:
        return (2, sorted(values, reverse=True))
    if count_vals[0] == 2:
        pair = max(v for v in counts if counts[v] == 2)
        kicker = max(v for v in counts if counts[v] == 1)
        return (1, pair, kicker)
    return (0, sorted(values, reverse=True))

def equity(hole, table):
    deck = [r+s for r in RANKS for s in SUITS]
    for c in hole:
        deck.remove(c)
    deck.remove(table)

    my = hand_rank(hole + [table])
    win = total = 0

    for opp in itertools.combinations(deck, 2):
        total += 1
        if my > hand_rank(list(opp) + [table]):
            win += 1

    return win / total

def decide_action(state):
    hole = state["your_hole"]
    table = state["table_card"]

    p = equity(hole, table)

    if p < 0.33:
        return "FOLD"
    elif p >= 0.66:
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
