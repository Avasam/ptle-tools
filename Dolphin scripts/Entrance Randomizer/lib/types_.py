from __future__ import annotations

from typing import Literal, TypeAlias

SeedType: TypeAlias = int | float | str | bytes | bytearray | Literal[False] | None
PriceRange: TypeAlias = tuple[int, int] | tuple[()] | Literal[False] | None
