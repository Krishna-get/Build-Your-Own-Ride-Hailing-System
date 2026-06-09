# starter/points.py
# Lat/lng pairs to use for your Week 3 deliverable.
#
# Use the pair for your city. If your city isn't listed, add your own
# using Google Maps (right-click any point → "What's here?").
#
# Format: (origin_lat, origin_lng, dest_lat, dest_lng, label)

ROUTE_PAIRS = {
    "hyderabad": (
        17.3850, 78.4867,   # Hyderabad city centre
        17.4239, 78.4738,   # Secunderabad
        "Hyderabad Centre → Secunderabad"
    ),
    "mumbai": (
        19.0760, 72.8777,   # Churchgate
        19.1136, 72.8697,   # Bandra
        "Churchgate → Bandra"
    ),
    "delhi": (
        28.6139, 77.2090,   # Connaught Place
        28.6562, 77.2410,   # Civil Lines
        "Connaught Place → Civil Lines"
    ),
    "bangalore": (
        12.9716, 77.5946,   # MG Road
        12.9352, 77.6245,   # Koramangala
        "MG Road → Koramangala"
    ),
    "london": (
        51.5074, -0.1278,   # Charing Cross
        51.5155, -0.0922,   # Aldgate
        "Charing Cross → Aldgate"
    ),
}

# Change this to your city
SELECTED_CITY = "hyderabad"

ORIGIN_LAT, ORIGIN_LNG, DEST_LAT, DEST_LNG, LABEL = ROUTE_PAIRS[SELECTED_CITY]
