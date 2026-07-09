# Week 7 Reflection

## Walk through the race condition in your own words
Imagine two independent passengers submit requests at the exact same millisecond, and our geospatial engine finds that `driver_042` is the closest vehicle for both. Without locking constraints, Server 1 checks the database and sees `driver_042` is `ONLINE`. At the exact same microsecond, Server 2 makes the same query and gets the same response. Both threads proceed to send a `ride_request` socket frame to the same driver. The driver will click "Accept" on one, but the system will double-book them, corrupting the state machine records and leaving one rider stranded.

## How does SET NX PX solve the race condition?
The `NX` directive acts as an atomic guard condition telling Redis to write the key only if it does not already exist. The first server thread to execute this primitive secures the key and acquires the lock, while any competing requests are instantly rejected with a `nil` return. The `PX` setting attaches an automated millisecond Time-To-Live (TTL) expiration to the lock, ensuring the driver state is released automatically if a process crashes.

## What happens if the server holding the lock crashes before releasing it?
If a server instance crashes or gets separated by a network partition, it will fail to hit the final `release_lock` clean-up code. Without an automated expiration, the system would permanently deadlock, and that driver would never be able to accept rides again. Thanks to the `PX` flag setting a 20-second TTL, Redis automatically evicts the stale token string out of memory, freeing the driver up for subsequent dispatch operations.

## Why do we use a Lua script to release the lock instead of just DEL?
Releasing a lock requires checking if we still own it before deleting it. If a server experiences a temporary garbage collection pause or network lag, its 20-second lock TTL might expire in Redis, allowing a second server to acquire the lock for a different ride request. If the first server wakes up and blindly calls `DEL`, it would delete the lock owned by the second server. A Lua script executes atomically on the Redis thread, ensuring we only delete the key if its value matches our unique UUID token string.

## Did your 15-second timeout re-match work correctly?
Yes, it works correctly. To simulate a driver not responding, I ran the dispatch engine loop without adding an acceptance trigger payload string into the `accept:{trip_id}:{driver_id}` cache coordinate. The system gracefully polled for 15 seconds, caught the lack of response, changed the current driver back to `ONLINE`, and immediately initiated a rematch iteration targeting the next closest driver.

## What state is the driver in after they decline or time out? Why?
The driver is reset back to the `ONLINE` state. This makes sure they return to the active matchmaking pool right away so they can receive other incoming ride requests, rather than being stuck in a dead state.

## In your own words: why did Uber move away from greedy nearest-driver matching?
Greedy nearest-driver matching is locally optimal but globally suboptimal. If the closest vehicle is immediately assigned to an incoming request, it can create a "wild goose chase" where a second rider appearing moments later is forced to wait for a driver much further away. By batching incoming requests over short windows (e.g., 500ms), the system can evaluate global linear assignments across a bipartite graph, minimizing the aggregate Estimated Time of Arrival (ETA) across all active users.

## How does this week connect to your Week 1 architecture diagram?
`dispatch.py` is the central orchestration engine of our platform. It sits directly beneath our API Gateway, acting as the operational bridge that coordinates geospatial queries against Redis, persists transactional state modifications inside PostgreSQL, and triggers real-time messaging events via the WebSocket bus layer.

## Time spent this week
4 hours

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| Redis SET NX PX — understand the lock primitive | 5 |
| Atomic lock release with Lua — understand why it's needed | 5 |
| Trip state machine — could implement all transitions from memory | 5 |
| Driver state machine — could implement all transitions from memory | 5 |
| 15-second timeout and re-match — working in my implementation | 5 |
| Greedy vs batched matching — understand the trade-off | 5 |