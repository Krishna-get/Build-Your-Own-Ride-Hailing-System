# Week 6 Reflection

> Fill this in after the two-server test passes.

---

## Did your two-server test pass? Describe what happened

<!-- Driver on port 8000, rider on port 8001 — did the rider receive updates? -->

---

## In your own words: why does the system break without Redis Pub/Sub?

<!-- What happens if you skip the Pub/Sub step and just use in-memory state? -->

---

## Why do we throttle to every 3 seconds instead of broadcasting every GPS tick?

<!-- What's the cost of broadcasting at full GPS frequency? -->

---

## What happens to a rider who disconnects and reconnects mid-trip?

<!-- Do they miss location updates? How would you handle that? -->

---

## Describe the WebSocket handshake in your own words

<!-- What HTTP headers are involved? What does 101 mean? -->

---

## How does this connect to the Week 1 architecture diagram?

<!-- Which component is this week's server.py? What does it connect to? -->

---

## Time spent this week

___ hours

---

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| HTTP polling vs SSE vs WebSockets — know the trade-offs | |
| WebSocket handshake — understand HTTP Upgrade | |
| Ping/pong keepalive — understand why it's needed | |
| Redis Pub/Sub — understand how it enables horizontal scaling | |
| Throttling — understand why and how to implement it | |
