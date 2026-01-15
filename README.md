# Quantitative Poker Bot

A probability-based poker bot for a simplified three-card poker game, designed to study
risk-aware decision making in a discrete, high-variance environment.

## Overview
- Uses exact hand equity computation (full enumeration, no Monte Carlo)
- Applies threshold-based decisions for stability
- Adapts aggression conservatively using opponent fold/raise frequencies
- Evaluated using a custom round-robin simulation engine

## Strategy (High-Level)
- Compute exact win probability for each hand
- Base decisions on equity thresholds (fold / call / raise)
- Slightly adjust thresholds in response to opponent behavior
- Avoid direct EV maximization to prevent instability

## Key Insight
Robust equity thresholds with small adaptive adjustments outperform direct expected-value
maximization in this discrete setting.

## Files
- `bot_final.py` – final adaptive bot
- `bot3_equity.py` – exact equity baseline strategy
- `bot2_threshold.py` – fixed threshold baseline
- `master_round_robin.py` – simulation framework

## How to Run
```bash
python master_round_robin.py
