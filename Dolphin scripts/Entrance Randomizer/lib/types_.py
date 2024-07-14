from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing import TypeAlias

    SeedType: TypeAlias = int | float | str | bytes | bytearray | Literal[False] | None
    PriceRange: TypeAlias = tuple[int, int] | tuple[()] | Literal[False] | None
else:
    SeedType = None
    PriceRange = None
