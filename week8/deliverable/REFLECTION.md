# Week 8 Reflection

## What is the economic objective of surge pricing?
The core objective of surge pricing is to rebalance a two-sided marketplace during unexpected supply/demand shocks. By raising prices dynamically when demand exceeds available driver capacity, the system creates two immediate market clearing effects: it filters out low-intent passengers to lower overall wait times, and it acts as a financial incentive that draws nearby offline drivers into the high-demand area to restore market equilibrium.

## Why use Uber H3 Resolution 8 instead of general city boundaries?
General city boundaries or polygon limits are too coarse and irregular to evaluate pricing shifts accurately. A demand spike at an airport or stadium would trigger price increases across an entire city quadrant, unfairly penalizing surrounding areas. H3 hexagons provide a perfectly uniform, high-resolution spatial grid. Resolution 8 breaks areas down into compact hexagons (~0.73 km²), allowing the pricing engine to contain surges precisely within localized neighborhoods.

## What is the risk of using non-atomic commands to update counters in Redis?
Under high throughput—such as thousands of concurrent users requesting rides at peak times—a non-atomic read-modify-write operation (`get` followed by `set`) creates severe race conditions. Two concurrent worker processes could read the exact same demand count value simultaneously, increment it locally, and write back the same number. This leads to lost updates and under-reported metrics, causing the system to completely miss genuine market surges. Atomic primitives like `INCR` bypass this by modifying the key directly on the single-threaded Redis execution pipeline.

## Why are TTL values critical on surge data keys?
Surge data represents a transient snapshot of current market conditions. If demand counters were stored indefinitely without a Time-To-Live (TTL) configuration, historic passenger search events would remain in memory forever. This would lead to permanent surge pricing in areas that are completely quiet, while also causing unbounded memory growth in the Redis cluster.

## Time spent this week
3 hours

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| Dynamic Market Equilibrium Theory | 5 |
| Uber H3 Hexagonal Cell Mapping Primitives | 5 |
| Thread-Safe Atomic Increments with Redis | 5 |
| Variable Multiplier Scaling Calculators | 5 |