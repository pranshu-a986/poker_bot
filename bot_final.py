import json
import sys
import itertools
import random
from collections import Counter

# --------------------------------
# Card utilities
# --------------------------------

RANKS = "23456789TJQKA"
SUITS = "CDHS"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}

def parse_card(card):
    return RANK_VALUE[card[0]], card[1]

# --------------------------------
# Hand evaluation (3-card poker)
# --------------------------------

def check_straight(values):
    values = sorted(values)
    if values == [2, 3, 14]:      # A-2-3
        return True, 3
    if values[0] + 1 == values[1] and values[1] + 1 == values[2]:
        return True, values[2]
    return False, 0

def hand_score(cards):
    values = []
    suits = []

    for c in cards:
        v, s = parse_card(c)
        values.append(v)
        suits.append(s)

    counts = Counter(values)
    count_values = sorted(counts.values(), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight, straight_high = check_straight(values)

    if is_flush and is_straight:
        return (5, straight_high)
    if count_values[0] == 3:
        return (4, max(values))
    if is_straight:
        return (3, straight_high)
    if is_flush:
        return (2, sorted(values, reverse=True))
    if count_values[0] == 2:
        pair = max(v for v in counts if counts[v] == 2)
        kicker = max(v for v in counts if counts[v] == 1)
        return (1, pair, kicker)
    return (0, sorted(values, reverse=True))

# --------------------------------
# Exact equity calculation
# --------------------------------

def calculate_equity(hole, table):
    deck = [r + s for r in RANKS for s in SUITS]
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

# --------------------------------
# Decision logic (ENHANCED VERSION)
# --------------------------------

def decide_action(state):
    hole = state["your_hole"]
    table = state["table_card"]

    opp = state.get("opponent_stats") or {}
    fold_count = opp.get("fold", 0)
    call_count = opp.get("call", 0)
    raise_count = opp.get("raise", 0)

    total_actions = fold_count + call_count + raise_count

    if total_actions == 0:
        p_fold = p_raise = 1 / 3
    else:
        p_fold = fold_count / total_actions
        p_raise = raise_count / total_actions

    equity = calculate_equity(hole, table)

    # -------- Base thresholds (tuned) --------
    fold_threshold = 0.25
    raise_threshold = 0.47   # slightly aggressive

    # -------- Maniac detection --------
    is_maniac = total_actions > 30 and p_raise > 0.80

    if is_maniac:
        # Respect maniacs, but don't freeze
        fold_threshold -= 0.06
        raise_threshold += 0.04
    else:
        # Passive opponent exploitation
        if p_fold > 0.42:
            raise_threshold -= 0.06
        if p_raise > 0.45:
            fold_threshold += 0.03
            raise_threshold += 0.03

    # ============================================
    # ENHANCEMENTS ADDED HERE
    # ============================================
    
    # 1. Enhanced exploitation of passive opponents
    if p_fold > 0.50 and equity > 0.35:
        # Bluff more against passive opponents (30% chance)
        if random.random() < 0.30:
            return "RAISE"
    
    # 2. Enhanced calling against aggressive opponents
    if p_raise > 0.40 and equity > 0.42:
        # Call more against aggression (catch bluffs)
        fold_threshold = max(0.15, fold_threshold - 0.10)
    
    # 3. Additional bluff-catching adjustment
    if p_raise > 0.35 and equity > 0.45:
        # Slightly lower folding threshold against moderate aggression
        fold_threshold = max(0.18, fold_threshold - 0.05)
    
    # ============================================
    # END ENHANCEMENTS
    # ============================================

    # Clamp thresholds (safety)
    fold_threshold = max(0.15, min(0.35, fold_threshold))
    raise_threshold = max(0.45, min(0.65, raise_threshold))

    # -------- Final decision --------

    # Light semi-bluff vs very passive opponents
    if equity >= 0.40 and p_fold > 0.55:
        return "RAISE"

    if equity < fold_threshold and not is_maniac:
        return "FOLD"
    elif equity >= raise_threshold:
        return "RAISE"
    else:
        return "CALL"

# --------------------------------
# I/O glue (DO NOT CHANGE)
# --------------------------------

def main():
    raw = sys.stdin.read().strip()
    try:
        state = json.loads(raw) if raw else {}
        action = decide_action(state)
    except Exception:
        action = "CALL"

    if action not in {"FOLD", "CALL", "RAISE"}:
        action = "CALL"

    sys.stdout.write(json.dumps({"action": action}))

if __name__ == "__main__":
    main()
