---
id: right-censoring
type: concept
title: Right-censoring
created: 2026-07-23
status: active
confidence: medium
publish: true
tags: [statistics, survival-analysis, lotclock]
---

# Right-censoring

An observation is **right-censored** when you know an event has not happened yet, but not when
it will. You watched for a while, the clock ran out, and the thing was still un-happened.

The classic case is medical survival analysis: a trial ends, some patients are still alive.
You do not know how long they lived — only that it was *at least* as long as you watched.

## Observations

- [claim] A right-censored record contributes real information: the event took **longer than** the observed window. It is not a missing value
- [gotcha] Deleting censored rows biases results toward short durations, because the long-lived cases are exactly the ones still un-resolved when you stop looking. The bias is systematic, not noise
- [gotcha] Filling censored durations with the observation-window length is worse than deleting them — it invents a false event and understates the tail
- [claim] Kaplan–Meier and Cox proportional hazards both handle censoring directly, by construction
- [claim] Standard regression on duration cannot handle censoring correctly without modification
- [question] All four claims above are textbook material I have not yet cited. Capture a survival-analysis reference into `raw/sources/` and promote them to `[fact]`
- [question] Which is more appropriate for LotClock: Kaplan–Meier for the descriptive curves, Cox for the covariate effects, or both for different outputs?

## Why it matters here

Every car listing still on sale on the last day of collection is right-censored. It has not
sold yet. Discarding those listings would make cars look like they sell faster than they do,
by systematically dropping the slow-moving ones — which is precisely the segment a liquidity
product exists to identify.

## Relations

- relates_to [[LotClock]]
- relates_to [[Survival Analysis]]
