---
id: lotclock-liquidity-over-price
type: decision
title: Measure liquidity, not price
created: 2026-07-19
updated: 2026-07-23
status: active
confidence: high
publish: true
tags: [lotclock, portfolio, framing, methodology]
---

# Measure liquidity, not price

LotClock started as a used-car price predictor. It became a liquidity tracker instead. This
note records why, because the original framing is the obvious one and the reasoning against it
is not.

## Observations

- [decision] LotClock measures days-to-sell and price cuts, not predicted sale price
- [because] A Malaysian listing price is an anchor, not a transaction — the real price is negotiated privately, so a price prediction can never be validated against ground truth
- [because] Price prediction is commoditised. Carsome does it with actual transaction data, which I cannot obtain, so competing there means losing on the one input that matters
- [because] Liquidity is directly observable from daily listing snapshots, and nobody publishes it
- [because] Measuring days-to-sell requires daily collection — a one-off scrape cannot observe a listing disappearing, so the target variable does not exist without it
- [because] That daily requirement is the moat. The dataset cannot be reproduced quickly by anyone starting later, which is why the scraper shipped before any model
- [gotcha] A listing that vanishes has not necessarily sold — it may have been withdrawn or expired. Disappearance is a censored observation, not a confirmed sale
- [question] How many days of collection before survival curves stabilise enough to be worth publishing?

## Relations

- part_of [[LotClock]]
- led_to [[Daily Scraper Architecture]]
- led_to [[Scraping Ethics Stance]]
- tests [[Right-Censoring]]
- relates_to [[Used Car Market Structure]]
