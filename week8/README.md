# Week 8 — Surge Pricing & Dynamic Pricing Logic

---

## 🎯 Goals

By the end of this week you should be able to:
- Explain the economic purpose of surge pricing in a two-sided marketplace (supply vs. demand equilibrium).
- Map real-world geographic coordinates to unique Uber H3 hexagonal spatial cells.
- Use atomic Redis operations (`INCR`, `DECR`, `EXPIRE`) to maintain thread-safe high-frequency supply/demand counters.
- Compute baseline fares using a standard travel metric formula: Time + Distance + Base Fees.
- Generate a dynamic surge multiplier based on localized supply-to-demand saturation ratios.

---

## 📚 Topics
1. **Marketplace Equilibrium:** Rebalancing supply and demand via price signaling.
2. **Hexagonal Aggregation:** Using Uber H3 cells (Resolution 8) to partition supply/demand zones uniformly.
3. **Atomic Counting:** Tracking transient events concurrently using Redis counters with time-to-live (TTL) expiration intervals.
4. **The Fare Formula:** Combining fixed costs, geographic distance (Haversine/OSM route lengths), and estimated durations.

---

## 💰 The Pricing Formula

Fares are computed dynamically using the standard ride-hailing architecture formula:

$$\text{Fare} = \left[ \text{Base Fare} + (\text{Per KM Rate} \times \text{Distance KM}) + (\text{Per Minute Rate} \times \text{Duration Minutes}) \right] \times \text{Surge Multiplier}$$

### Surge Multiplier Logic:
- Calculate the Supply/Demand ratio inside a rider's origin H3 cell.
- If $\text{Demand} \ge \text{Supply}$, scale the surge multiplier up continuously up to a maximum cap (e.g., $3.0\times$).
- If $\text{Supply} > \text{Demand}$ or fields are balanced, the multiplier remains at baseline ($1.0\times$).