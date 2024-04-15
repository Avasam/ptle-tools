from __future__ import annotations

from typing import Literal

from types_ import SeedType

SEED: SeedType = None
"""
Set your own seed, can be an `int`, `float`, `str`, `bytes` or `bytearray`.

Use `None` or any Falsy value to generate a random seed.
"""

STARTING_AREA: int | None = None
"""
The ID of the Area to start in. `None` for random, `0xEE8F6900` for Crash Site.

See `transition_infos.json` for all available IDs
"""

LINKED_TRANSITIONS: bool = False
"""
Whether the new destination will contain an exit back to the area you came from.
Assuming both areas have as many entrances as they have exits.
"""

DISABLE_MAPS_IN_SHOP: bool = False
"""
Whether you can buy maps in the Shaman Shop.
When maps are disabled, and using original shop prices, the 4 lowest prices (0, 1, 2, 2) are also removed form the pool.
"""

SHOP_PRICES_RANGE: tuple[int, int] | Literal[False] = (0, 32)  # False
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

Use `False` to shuffle around original shop prices.
"""
