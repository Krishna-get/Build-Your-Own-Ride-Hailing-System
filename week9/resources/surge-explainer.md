# Surge Pricing & Spatial Aggregation — Explainer

---

## The Economics of Surge

In a classic marketplace, a sudden influx of buyers causes prices to adjust upward until demand matches supply. In a ride-hailing system, this has two direct real-world impacts:
1. **Suppression of Demand:** Riders who don't urgently need a ride decide to wait or choose alternative transit options, leaving vehicles open for high-intent users.
2. **Incentivization of Supply:** Drivers on the app see the high multiplier zones on their map and physically migrate to that neighborhood to capitalize on higher earnings, resolving the shortage.

---

## Why Hexagons (H3)?

If we tracked supply and demand at a city-wide level, a concert letting out downtown would cause ride costs to spike for someone trying to go home from a quiet suburb 15 kilometers away. 

By grouping tracking boundaries into **H3 Resolution 8 Hexagons** (each covering roughly 0.73 square kilometers), we isolate the economic calculations onto small footprints. This allows the system to establish hyper-localized pricing changes without impacting neighboring blocks.