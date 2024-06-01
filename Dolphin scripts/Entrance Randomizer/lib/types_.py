from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Tuple, Union

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    SeedType: TypeAlias = Union[int, float, str, bytes, bytearray, Literal[False], None]
    PriceRange: TypeAlias = Union[Tuple[int, int], Tuple[()], Literal[False], None]
else:
    SeedType = None
    PriceRange = None
