# Week 1 — System Design Foundations & The Big Picture

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🎯 Goals

By the end of this week you should be able to:

- Explain the core services inside an Uber-like system and why each exists
- Distinguish between monolithic and microservice architectures and articulate the trade-offs
- Define latency, throughput, and availability — and explain what "real-time" actually means
- Apply the CAP theorem to a distributed system and reason about trade-offs
- Produce a clear, labelled architecture diagram with correct data-flow arrows

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | Monolith vs microservices — trade-offs, when each makes sense |
| 2 | Core services in Uber-like apps: Rider, Driver, Dispatch/Matching, Pricing, Trip, Payments, Maps |
| 3 | Latency, throughput, availability — what "real-time" really means in practice |
| 4 | Sketching architecture diagrams: boxes, arrows, data flow |
| 5 | CAP theorem basics: consistency, availability, partition tolerance |

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Uber Engineering Blog — architecture deep-dives | https://www.uber.com/en-IN/blog/engineering/ |
| System Design Primer — Donne Martin (GitHub) | https://github.com/donnemartin/system-design-primer |
| System Design: Uber (FAANG Senior Engineer) | https://www.youtube.com/watch?v=ZRAE0fUvN_M |
| CAP Theorem Explained — Martin Kleppmann | https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html |

### Recommended Book
> **System Design Interview Vol. 1** — Alex Xu.  
> Chapters 1–3 (scale, estimation, and the interview framework) are directly relevant this week. The book covers rate limiters, consistent hashing, key-value stores, and other distributed systems patterns you'll encounter throughout this roadmap.

---

## ⭐ Deliverable

> **Do not skip this. It is proof you learned the week.**

### Architecture Diagram

Create a **one-page architecture diagram** of your planned mini ride-hailing system using [Excalidraw](https://excalidraw.com) or [draw.io](https://draw.io).

**Requirements — your diagram MUST include all of the following:**

| Component | Notes |
|-----------|-------|
| 🧑 Rider App | Mobile/web client |
| 🚗 Driver App | Mobile client |
| 🔀 API Gateway | Single entry point, handles auth |
| 📡 Dispatch Service | Matching riders ↔ drivers |
| 💰 Pricing Service | Base fare + surge calculation |
| 🗺️ Trip Service | Lifecycle management |
| 🗺️ Map / Routing Service | A* routing, geospatial queries |
| 🐘 PostgreSQL | Primary relational datastore |
| ⚡ Redis | Caching, Pub/Sub, geospatial index |

**Each service must have:**
- A clear label
- Arrows showing which direction data flows
- A brief (2–5 word) annotation on each arrow (e.g. "JWT auth request", "driver lat/lng update")

### Submission Checklist

- [ ] Diagram exported as PNG or PDF and placed in the `/diagrams/` folder
- [ ] All 9 components present and labelled
- [ ] All arrows annotated with data-flow descriptions
- [ ] A short `REFLECTION.md` (see template below) completed and committed

---

## 📝 Reflection Template

Fill in `/diagrams/REFLECTION.md` after completing the deliverable:

```markdown
# Week 1 Reflection

## What surprised me most about the architecture
(2–3 sentences)

## The hardest trade-off I had to think through
(e.g. monolith vs microservices for a first version — what did you decide and why?)

## One question I still have
(Write it down — you will likely answer it by Week 9)

## Time spent this week
___ hours
```

---

## 🗂️ Folder Structure

```
week1-system-design/
├── README.md               ← You are here
├── diagrams/
│   ├── architecture.png    ← Your deliverable goes here
│   └── REFLECTION.md       ← Your reflection goes here
├── resources/
│   ├── cap-theorem.md      ← Cheat-sheet notes (provided)
│   ├── monolith-vs-microservices.md
│   └── service-glossary.md
└── starter/
    └── excalidraw-template.excalidraw  ← Optional starter template
```

---

## 💡 Study Tips

- **Don't just read** — draw the diagram *before* reading the resources, then revise it after. The delta between your first and final draft is your learning.
- **Timebox** — spend no more than 2 hours reading; the rest of your 8 hours should be on the diagram and reflection.
- **The CAP theorem is subtle** — focus on understanding *why* you can't have all three, not memorising the definition.

---

## ⏭️ What's Next

**Week 2 — Graphs & Dijkstra's Algorithm**  
You'll build the algorithmic foundation that every routing engine sits on — implementing Dijkstra from scratch using a min-heap.

---

*Engineering Behind Ride-Hailing & Mapping Systems · Week 1 of 9*
