# Week 1 Reflection

## What surprised me most about the architecture

My instinct was that driver locations would be stored in the main database alongside everything else. What changed my thinking was realising that a driver's GPS position updates every 2–4 seconds — that is thousands of writes per minute across all active drivers. PostgreSQL is built for durable, consistent records like trip history and payments; hammering it with high-frequency location pings would be slow and wasteful. Redis handles this instead because it lives in memory, supports geospatial indexing natively, and can absorb the write volume without breaking a sweat. The database never needs to know where a driver is *right now* — only where they *were* when a trip was completed.

## The hardest trade-off I had to think through

Applying the CAP theorem to different parts of the same system was harder than I expected. It is not a single choice you make once — different services need different guarantees. For payment processing, consistency is non-negotiable: charging a rider twice or missing a charge is a real business problem, so PostgreSQL in CP mode is the right call even if it means occasional slowness. For driver locations and surge pricing display, a slightly stale value is completely acceptable — a driver shown 300 metres from where they actually are is fine. Those services can favour availability over strict consistency. The insight is that "what does the user actually notice if this data is 2 seconds old?" is the right question to ask for each service individually.

## One question I still have

The Dispatch service has to find the nearest available driver in real time. Redis geospatial queries give us candidate drivers nearby — but how does the matching algorithm decide *which* driver to assign when there are multiple good options? Is it purely closest distance, or does it factor in driver rating, route efficiency, or predicted acceptance rate? I suspect by Week 9 the routing and optimisation work will answer this.

## Time spent this week

1–2 hours
