# Week 4 Reflection

> Fill this in after your nearby-drivers service hits the under-50ms target.

---

## Which approach did you use? Why?

<!-- Redis GEOSEARCH / your own H3 k-ring / your own geohash prefix -->

---

## What was your measured query time?

Average over 100 runs: ___ ms

---

## In your own words: why does bucketing beat scanning all drivers?

<!-- 2–3 sentences -->

---

## Describe the boundary edge case in your own words

<!-- What goes wrong if you only search the exact matching cell, with no neighbours? -->

---

## Why does Uber use hexagons instead of squares for H3?

<!-- Explain the equidistant-neighbour property -->

---

## What resolution / precision did you choose, and why?

<!-- Too coarse = too many candidates to rank. Too fine = might miss nearby drivers
in an adjacent cell. What tradeoff did you land on? -->

---

## How does this connect to the dispatch service in your Week 1 architecture?

---

## Time spent this week

___ hours

---

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| Geohash encoding and prefix search | |
| The boundary-straddling edge case and its fix | |
| Quadtrees / R-trees — conceptual understanding | |
| H3 hexagons — why they're used and how k-ring works | |
| Could explain "why not just scan all drivers" to a non-technical person | |
