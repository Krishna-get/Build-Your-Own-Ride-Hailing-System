# Week 6 Reflection

## Did your two-server test pass? Describe what happened
Yes, the horizontal verification test passed perfectly! I ran Server 1 on port `8000` and Server 2 on port `8001` inside separate terminals. When connecting the simulated driver client to port `8000` and opening a test rider client connection listening on port `8001`, the rider successfully received real-time driver coordinates. The location data correctly crossed the boundary between the isolated node processes via Redis Pub/Sub channels without losing telemetry frames.

## In your own words: why does the system break without Redis Pub/Sub?
Without Redis Pub/Sub, each server process relies strictly on local, in-memory context stores to map connected user clients. If a rider lands on Server 2 while their matched driver is streaming location packets into a WebSocket terminal attached to Server 1, the systems are completely blind to one another. Bypassing a distributed messaging broker completely limits system capacity to a single, fragile monolithic instance, preventing horizontal cluster scaling.

## Why do we throttle to every 3 seconds instead of broadcasting every GPS tick?
Broadcasting every atomic hardware GPS update creates excessive computational overhead for the network, servers, and clients. Mobile device location ticks can fire several times a second, meaning that thousands of unthrottled active drivers would hit the system with heavy read/write volumes. Throttling updates to 3-second windows reduces network throughput demands by roughly 6x, conserving battery life on mobile apps and reducing unnecessary downstream connection stress while keeping UI car marker transitions perfectly smooth.

## What happens to a rider who disconnects and reconnects mid-trip?
Because Redis Pub/Sub acts as an ephemeral, fire-and-forget messaging layer with no native message state storage, any location frame emitted while the rider is shifting cellular bands or reconnecting is dropped. However, this is perfectly fine for live tracking. As soon as the rider reconnects to the `/ws/rider/{trip_id}` route, the lifecycle server spins up a fresh background Pub/Sub subscription task, and the rider gets the newest location update within 3 seconds.

## Describe the WebSocket handshake in your own words
A WebSocket connection begins as a standard HTTP/1.1 request initiated by the client, containing an explicit `Upgrade: websocket` header alongside a unique cryptographic string key named `Sec-WebSocket-Key`. If the backend application accepts the persistent request, it responds with an `HTTP 101 Switching Protocols` status code status change block. This tells both network layers to keep the underlying TCP socket channel fully open, abandoning the classical request-response framework in favor of long-lived, bidirectional binary framing streams.

## How does this connect to the Week 1 architecture diagram?
This server script acts directly as the scalable gateway router underpinning both our Gateway layer and our real-time notification framework. It interacts closely with our Driver/Rider app components on the frontend while acting as a direct streaming client to Redis. By handling telemetry ingest and distribution asynchronously, it keeps high-frequency position data completely away from the primary PostgreSQL database tables.

## Time spent this week
3 hours

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| HTTP polling vs SSE vs WebSockets — know the trade-offs | 5 |
| WebSocket handshake — understand HTTP Upgrade | 5 |
| Ping/pong keepalive — understand why it's needed | 5 |
| Redis Pub/Sub — understand how it enables horizontal scaling | 5 |
| Throttling — understand why and how to implement it | 5 |