# Week 7 Reflection

> This is the most complex week. Take time to reflect carefully.

---

## Walk through the race condition in your own words

<!-- Two riders, one driver, no lock — what goes wrong exactly? -->

---

## How does SET NX PX solve the race condition?

<!-- Explain what NX does and why the TTL matters -->

---

## What happens if the server holding the lock crashes before releasing it?

<!-- How does the TTL protect against this? -->

---

## Why do we use a Lua script to release the lock instead of just DEL?

<!-- Describe the race condition that Lua prevents -->

---

## Did your 15-second timeout re-match work correctly?

<!-- Describe your test: how did you simulate a driver not responding? -->

---

## What state is the driver in after they decline or time out? Why?

---

## In your own words: why did Uber move away from greedy nearest-driver matching?

<!-- Describe the "wild goose chase" problem -->

---

## How does this week connect to your Week 1 architecture diagram?

<!-- Which box is dispatch.py? What does it talk to? -->

---

## Time spent this week

___ hours

---

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| Redis SET NX PX — understand the lock primitive | |
| Atomic lock release with Lua — understand why it's needed | |
| Trip state machine — could implement all transitions from memory | |
| Driver state machine — could implement all transitions from memory | |
| 15-second timeout and re-match — working in my implementation | |
| Greedy vs batched matching — understand the trade-off | |
