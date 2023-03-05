from __future__ import annotations

from types_ import SeedType

SEED: SeedType = None
"""
Set your own seed, can be an `int`, `float`, `str`, `bytes` or `bytearray`.

`None` or any Falsy value to generate a random seed.
"""

STARTING_AREA: int | None = None
"""
The ID of the Area to start in. `None` for random, `0xEE8F6900` for Crash Site.

See `transition_infos.json` for all available IDs
"""
