---
id: purityloop-small-object-blindness
type: experiment
title: The bottleneck is small objects, not class confusion
created: 2026-07-19
updated: 2026-07-23
status: active
confidence: high
publish: false
sources: [raw/sources/jobs-4242-4247-recall-by-area.md]
tags: [capstone, purityloop, yolo, segmentation, root-cause]
---

# The bottleneck is small objects, not class confusion

Recall broken down by object area and by scene density, measured on the full validation set
(jobs 4242 and 4247). Run to settle whether PurityLoop's ceiling was a model problem or a data
problem.

## Observations

- [result] Recall by object area — tiny (<1% of frame) 0.188 | small (1–5%) 0.366 | medium 0.560 | large 0.637 | huge (>50%) 0.778
- [result] Recall by scene density — 1 object 0.835 | 2–5 objects 0.512 | 6+ objects 0.391
- [result] Median object occupies 6.8% of the frame
- [fact] Every class-versus-class confusion cell is ≤ 0.04 — the model is not mixing classes up #verified
- [fact] Between 25% and 47% of each class is lost to background, not to another class
- [fact] Once an object is detected, classification is ~91% correct
- [because] Taken together: the model can tell the classes apart. It cannot *find* the objects. The failure is detection recall on small, densely-packed instances
- [gotcha] Aggregate mAP hides this completely. The single number looked like a mediocre model; the breakdown showed a specific, addressable failure mode
- [question] Does raising input resolution recover tiny-object recall, or is the annotation itself too coarse at that scale?

## Relations

- part_of [[PurityLoop]]
- tests [[Small Object Detection]]
- led_to [[Dataset Is The Bottleneck]]
- relates_to [[PurityLoop Run History]]
