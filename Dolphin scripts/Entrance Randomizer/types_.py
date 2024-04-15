from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Union

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    SeedType: TypeAlias = Union[int, float, str, bytes, bytearray, Literal[False], None]
else:
    SeedType = None
