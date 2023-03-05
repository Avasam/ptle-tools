from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    SeedType: TypeAlias = Union[int, float, str, bytes, bytearray, None]
else:
    SeedType = None
