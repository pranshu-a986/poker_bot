import json
import subprocess
import random
from collections import defaultdict

RANKS = "23456789TJQKA"
SUITS = "CDHS"

def random_card(exclude):
    deck = [r+s for r in RANKS for s in SUITS if r+s not in exclude]
    return random.choice(deck)

def run_bot(bot_file, state):
    p = subprocess.Popen(
        ["python", bot_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate(json.dumps(state), timeout=1)
    if err:
        raise RuntimeError(err)
    return json.loads(out)["action"]

def play(botA, botB, rounds=1001):
    scoreA = scoreB = 0
    statsA = defaultdict(int)
    statsB = defaultdict(int)

    opp_stats_A = defaultdict(int)
    opp_stats_B = defaultdict(int)

    for r in range(1, rounds + 1):
        c1 = random.choice(RANKS) + random.choice(SUITS)
        c2 = random.choice([r+s for r in RANKS for s in SUITS if r+s != c1])
        table = random.choice([r+s for r in RANKS for s in SUITS if r+s not in {c1, c2}])

        stateA = {
            "your_hole": [c1, c2],
            "table_card": table,
            "opponent_stats": opp_stats_A,
            "round": r
        }
        stateB = {
            "your_hole": [c1, c2],
            "table_card": table,
            "opponent_stats": opp_stats_B,
            "round": r
        }

        aA = run_bot(botA, stateA)
        aB = run_bot(botB, stateB)

        statsA[aA.lower()] += 1
        statsB[aB.lower()] += 1

        opp_stats_A[aB.lower()] += 1
        opp_stats_B[aA.lower()] += 1

        payoff = {
            ("FOLD","CALL"): (-1,2),
            ("FOLD","RAISE"): (-1,3),
            ("CALL","FOLD"): (2,-1),
            ("RAISE","FOLD"): (3,-1),
            ("CALL","CALL"): (0,0),
            ("CALL","RAISE"): (0,0),
            ("RAISE","CALL"): (0,0),
            ("RAISE","RAISE"): (0,0),
            ("FOLD","FOLD"): (0,0)
        }

        sA, sB = payoff.get((aA,aB),(0,0))
        scoreA += sA
        scoreB += sB

    print(f"\n{botA} vs {botB} ({rounds} hands)")
    print(f"Score: {scoreA} vs {scoreB}")
    print("Actions A:", dict(statsA))
    print("Actions B:", dict(statsB))

if __name__ == "__main__":
    play("bot_final.py", "bot2_threshold.py")
    play("bot_final.py", "bot3_equity.py")
    play("bot2_threshold.py", "bot3_equity.py")
