# Week 9 Reflection

## What is the main problem Docker solves for production architectures?
Docker solves the "it works on my machine" crisis by freezing the entire runtime system environment—including the operating system kernel footprint, package dependencies, binaries, and configurations—into an immutable container image. This eliminates any drift between local Windows environments and cloud Linux infrastructure.

## Why use named volumes for PostgreSQL instead of leaving storage inside the container?
Containers are completely ephemeral by design; if a container crashes, updates, or gets recreated, its internal scratch space storage is instantly wiped out. A named volume mounts a designated directory from the host machine's persistent file system right into the PostgreSQL data directory inside the container, ensuring transaction histories and client accounts survive safely across container life cycles.

## How do internal container networks improve system security?
By default, services connected to a Docker bridge network communicate using internal container DNS naming lookups (e.g., matching `redis:6379` or `postgres:5432`) completely isolated from the outside world. This allows backend architectures to communicate securely over local channels, ensuring databases are never exposed to public internet attack surfaces.

## Time spent this week
2 hours

## Self-assessment

| Topic | Rating (1–5) |
|-------|-------------|
| Multi-Container Orchestration Flow | 5 |
| Stateful vs Ephemeral Storage Volume Bindings | 5 |
| Network Bridge Isolation Security Frameworks | 5 |