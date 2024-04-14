from __future__ import annotations

from dataclasses import dataclass
from itertools import chain

from dolphin import memory  # pyright: ignore[reportMissingModuleSource]
from transition_infos import transition_infos


@dataclass
class Addresses:
    version_string: str
    prev_area: list[int]
    current_area: int
    item_swap: int


DRAW_TEXT_STEP = 24
DRAW_TEXT_OFFSET_X = 272

TRANSITION_INFOS_DICT = {
    area.area_id: area for area in chain(*transition_infos)
}
ALL_TRANSITION_AREAS = {area.area_id for area in chain(*transition_infos)}
ALL_POSSIBLE_EXITS = [
    exit_.area_id for exit_ in chain(
        *(area.exits for area in TRANSITION_INFOS_DICT.values()),
    )
]

_game_id_base = "".join([
    chr(memory.read_u8(0x80000000 + i))
    for i in range(3)
])
GAME_REGION = chr(memory.read_u8(0x80000003))
_developer_id = "".join([
    chr(memory.read_u8(0x80000004 + i))
    for i in range(2)
])
GAME_VERSION = memory.read_u8(0x80000007)
IS_GC = _game_id_base == "GPH"
IS_WII = _game_id_base == "RPF"

# Including the version number seems overkill, I don't think there was ever a non v0. Can add later if needed.
if GAME_VERSION != 0:
    raise Exception(f"Unknown game version {GAME_VERSION}!")
_addresses_map = {
    "GPH": {
        "D": Addresses("GC DE 0-00", [0x80747648], 0x80417F50, 0x804C7734),
        "E": Addresses("GC US 0-00", [0x8072B648], 0x8041BEB4, 0x804CB694),
        "F": Addresses("GC FR 0-00", [0x80747648], 0x80417F30, 0x804C7714),
        "P": Addresses("GC EU 0-00", [0x80747648], 0x80417F10, 0x804C76F4),
    },
    "RPF": {
        "E": Addresses("Wii US 0-00", [0x804542DC, 0x8], 0x80448D04, 0x80446608),
        "P": Addresses("Wii EU 0-00", [0x804546DC, 0x18], 0x80449104, 0x80446A08),
    },
}

_addresses = _addresses_map.get(_game_id_base, {}).get(GAME_REGION)
if not _addresses or _developer_id != "52":
    raise Exception(
        "Unknown version of Pitfall The Lost Expedition "
        + f"(game id -> {_game_id_base}{GAME_REGION}{_developer_id}, version -> {GAME_VERSION})",
    )
print(f"Detected {_addresses.version_string} version!")

PREV_AREA_ADDR = _addresses.prev_area
CURRENT_AREA_ADDR = _addresses.current_area
ITEM_SWAP_ADDR = _addresses.item_swap

JAGUAR = 0x99885996
CRASH_SITE = 0xEE8F6900
PLANE_COCKPIT = 0x4A3E4058
CHAMELEON_TEMPLE = 0x0081082C
JUNGLE_CANYON = 0xDEDA69BC
MAMA_OULLO_TOWER = 0x07ECCC35
VIRACOCHA_MONOLITHS = 0x6F498BBD
VIRACOCHA_MONOLITHS_CUTSCENE = 0xE8362F5F
ALTAR_OF_AGES = 0xABD7CCD8
BITTENBINDERS_CAMP = 0x0EF63551
MYSTERIOUS_TEMPLE = 0x099BF148
APU_ILLAPU_SHRINE = 0x5511C46C
SCORPION_TEMPLE = 0x4B08BBEB
ST_CLAIRE_NIGHT = 0x72AD42FA
ST_CLAIRE_DAY = 0x72AD42FA
TELEPORTERS = 0xE97CB47C

GC_MIN_ADDRESS = 0x80000000
GC_MEM_SIZE = 0x1800000
GC_MAX_ADDRESS = 0x80000000 + GC_MEM_SIZE - 1  # so 0x817FFFFF
