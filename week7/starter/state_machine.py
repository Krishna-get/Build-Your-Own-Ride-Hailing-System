"""
starter/state_machine.py
=========================
Trip and driver state machine constants, transitions, and validation helpers.

Import these into your deliverable/dispatch.py to avoid hardcoding strings.
"""

# ── Trip states ────────────────────────────────────────────────────────────────

class TripStatus:
    REQUESTED      = "REQUESTED"
    MATCHING       = "MATCHING"
    PENDING_ACCEPT = "PENDING_ACCEPT"
    ACCEPTED       = "ACCEPTED"
    EN_ROUTE       = "EN_ROUTE"
    IN_TRIP        = "IN_TRIP"
    COMPLETED      = "COMPLETED"
    RATED          = "RATED"
    CANCELLED      = "CANCELLED"


# Valid transitions: {current_state: [allowed_next_states]}
TRIP_TRANSITIONS = {
    TripStatus.REQUESTED:      [TripStatus.MATCHING, TripStatus.CANCELLED],
    TripStatus.MATCHING:       [TripStatus.PENDING_ACCEPT, TripStatus.CANCELLED],
    TripStatus.PENDING_ACCEPT: [TripStatus.ACCEPTED, TripStatus.MATCHING],   # re-match on timeout
    TripStatus.ACCEPTED:       [TripStatus.EN_ROUTE, TripStatus.CANCELLED],
    TripStatus.EN_ROUTE:       [TripStatus.IN_TRIP],
    TripStatus.IN_TRIP:        [TripStatus.COMPLETED],
    TripStatus.COMPLETED:      [TripStatus.RATED],
    TripStatus.RATED:          [],
    TripStatus.CANCELLED:      [],
}

# Timeout in seconds for states that have them (None = no timeout)
TRIP_TIMEOUTS = {
    TripStatus.REQUESTED:      30,
    TripStatus.MATCHING:       30,
    TripStatus.PENDING_ACCEPT: 15,   # driver must accept within 15 seconds
    TripStatus.ACCEPTED:       None,
    TripStatus.EN_ROUTE:       None,
    TripStatus.IN_TRIP:        None,
    TripStatus.COMPLETED:      None,
    TripStatus.RATED:          None,
    TripStatus.CANCELLED:      None,
}


# ── Driver states ──────────────────────────────────────────────────────────────

class DriverStatus:
    OFFLINE        = "OFFLINE"
    ONLINE         = "ONLINE"
    PENDING_ACCEPT = "PENDING_ACCEPT"   # received request, deciding
    EN_ROUTE       = "EN_ROUTE"         # accepted, heading to pickup
    ON_TRIP        = "ON_TRIP"          # passenger in car
    COMPLETED      = "COMPLETED"        # just finished, returning to ONLINE


DRIVER_TRANSITIONS = {
    DriverStatus.OFFLINE:        [DriverStatus.ONLINE],
    DriverStatus.ONLINE:         [DriverStatus.PENDING_ACCEPT, DriverStatus.OFFLINE],
    DriverStatus.PENDING_ACCEPT: [DriverStatus.EN_ROUTE, DriverStatus.ONLINE],   # ONLINE on decline/timeout
    DriverStatus.EN_ROUTE:       [DriverStatus.ON_TRIP],
    DriverStatus.ON_TRIP:        [DriverStatus.COMPLETED],
    DriverStatus.COMPLETED:      [DriverStatus.ONLINE],
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def is_valid_trip_transition(current: str, next_state: str) -> bool:
    """Return True if transitioning from current → next_state is allowed."""
    return next_state in TRIP_TRANSITIONS.get(current, [])


def is_valid_driver_transition(current: str, next_state: str) -> bool:
    """Return True if transitioning from current → next_state is allowed."""
    return next_state in DRIVER_TRANSITIONS.get(current, [])


def validate_trip_transition(current: str, next_state: str) -> None:
    """
    Raise ValueError if the transition is not allowed.
    Use this as a guard before updating the database.
    """
    if not is_valid_trip_transition(current, next_state):
        raise ValueError(
            f"Invalid trip transition: {current} → {next_state}. "
            f"Allowed: {TRIP_TRANSITIONS.get(current, [])}"
        )


# ── WebSocket message types ────────────────────────────────────────────────────

class WSMessageType:
    # Server → Driver
    RIDE_REQUEST   = "ride_request"      # new trip available
    RIDE_CANCELLED = "ride_cancelled"    # rider cancelled before accept

    # Server → Rider
    DRIVER_ASSIGNED  = "driver_assigned"   # driver accepted
    NO_DRIVER_FOUND  = "no_driver_found"   # all drivers declined/timed out
    DRIVER_EN_ROUTE  = "driver_en_route"   # driver is on the way
    TRIP_STARTED     = "trip_started"      # pickup confirmed
    TRIP_COMPLETED   = "trip_completed"    # drop-off confirmed

    # Bidirectional
    PING = "ping"
    PONG = "pong"
