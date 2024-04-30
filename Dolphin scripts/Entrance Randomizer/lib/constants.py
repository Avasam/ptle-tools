from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from itertools import chain

import CONFIGS
from dolphin import memory  # pyright: ignore[reportMissingModuleSource]
from lib.transition_infos import transition_infos

__version__ = "0.3.3"
"""
Major: New major feature or functionality

Minor: Affects seed

Patch: Does't affect seed (assuming same settings)
"""
print(f"Python version: {sys.version}")
print(f"Rando version: {__version__}")

# Sets the seed
seed = CONFIGS.SEED if CONFIGS.SEED else random.randrange(sys.maxsize)
random.seed(seed)
seed_string = hex(seed).upper() if isinstance(seed, int) else seed
print("Seed set to:", seed_string)


@dataclass
class Addresses:
    version_string: str
    prev_area: list[int]
    current_area: int
    item_swap: int
    shaman_shop_struct: int


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

TODO = 0x0

# Including the version number seems overkill, I don't think there was ever a non v0. Can add later if needed.
if GAME_VERSION != 0:
    raise Exception(f"Unknown game version {GAME_VERSION}!")
_addresses_map = {
    "GPH": {
        "D": Addresses("GC DE 0-00", [0x80747648], 0x80417F50, 0x804C7734, TODO),
        "E": Addresses("GC US 0-00", [0x8072B648], 0x8041BEB4, 0x804CB694, 0x7E00955C),
        "F": Addresses("GC FR 0-00", [0x80747648], 0x80417F30, 0x804C7714, TODO),
        "P": Addresses("GC EU 0-00", [0x80747648], 0x80417F10, 0x804C76F4, TODO),
    },
    "RPF": {
        "E": Addresses("Wii US 0-00", [0x804542DC, 0x8], 0x80448D04, 0x80446608, TODO),
        "P": Addresses("Wii EU 0-00", [0x804546DC, 0x18], 0x80449104, 0x80446A08, TODO),
    },
}

_addresses = _addresses_map.get(_game_id_base, {}).get(GAME_REGION)
if not _addresses or _developer_id != "52":
    raise Exception(
        "Unknown version of Pitfall The Lost Expedition "
        + f"(game id -> {_game_id_base}{GAME_REGION}{_developer_id}, version -> {GAME_VERSION})",
    )

ADDRESSES = _addresses
print(f"Detected {ADDRESSES.version_string} version!")

# Level CRCs
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
