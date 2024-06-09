from __future__ import annotations

from lib.types_ import PriceRange, SeedType

SEED: SeedType = None
"""
Set your own seed, can be an `int`, `float`, `str`, `bytes` or `bytearray`.

Use `None` or any Falsy value to generate a random seed.

default = None
"""

STARTING_AREA: int | None = None
"""
The ID of the Area to start in. `None` for random, `0xEE8F6900` for Crash Site.

See `transition_infos.json` for all available IDs.

default = None
"""

LINKED_TRANSITIONS: bool = True
"""
If True, going through any given transition and then backing out
will always result in you returning to the area you came from.
If False, no such guarantees are given.

default = True
"""

SKIP_JAGUAR: bool = True
"""
If True, you will completely skip both Jaguar fights.
If False, you will fight Jaguar 1 when you start a New Game (and go to STARTING_AREA afterwards),
and you will fight Jaguar 2 before fighting Pusca.

default = True
"""

DISABLE_MAPS_IN_SHOP: bool = True
"""
Whether you can buy maps in the Shaman Shop.

When maps are disabled and using original shop prices,
the 4 lowest prices (0, 1, 2, 2) are also removed from the pool.

default = True
"""

SHOP_PRICES_RANGE: PriceRange = False  # (0, 32)
"""
The range of prices for randomized Shaman Shop prices.

The value is a 2-item `tuple` of values between 0-138,
representing a range between the minimum and maximum possible prices for any item.
If you set the initial "minimum" too high, it'll be clamped down.
If you set the initial "maximum" too low, it'll be clamped up.

The distribution is biased towards the start of the range,
but tries to avoid repeating numbers at the extremities of the range,
and the total is ensured to always be 138 idols.
So it's possible for your "minimum" price to not be respected based on RNG.

Use `False` or `()` to shuffle around original shop prices.

default = False  # (0, 32)
"""
