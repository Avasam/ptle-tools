from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from enum import IntEnum
from itertools import chain

import CONFIGS
from dolphin import memory  # pyright: ignore[reportMissingModuleSource]
from lib.transition_infos import transition_infos

__version = "0.4.0"
"""See CHANGELOG.md for version semantics."""
__dev_version = "local"
__version__ = f"{__version}-{__dev_version}"
print(f"Python version: {sys.version}")
print(f"Rando version: {__version__}")

# Sets the seed
seed = CONFIGS.SEED or random.randrange(sys.maxsize)
random.seed(seed)
seed_string = hex(seed).upper() if isinstance(seed, int) else seed
print("Seed set to:", seed_string)


@dataclass(frozen=True)
class Addresses:
    version_string: str
    previous_area_blocks_ptr: int
    current_area: int
    area_load_state: int
    player_ptr: int

    item_swap: int
    shaman_shop_struct: int
    backpack_struct: int
    """Same address as Slingshot"""


class BackpackOffset(IntEnum):
    Canteen = 196
    Slingshot = 0
    Torch = 28
    Shield = 112
    GasMask = 168
    Raft = 140
    Pickaxes = 56
    TNT = 84


class PlayerPtrOffset(IntEnum):
    PositionX = 0x338
    PositionY = 0x33C
    PositionZ = 0x340
    CollideState = 0x3D0

    RisingStrike = 0x1960
    SmashStrike = 0x1988
    Breakdance = 0x1970
    HeroicDash = 0x1978
    HeroicDive = 0x1980
    SuperSling = 0x1968


TRANSITION_INFOS_DICT = {
    area.area_id: area for area in chain(*transition_infos)
}
ALL_TRANSITION_AREAS = frozenset(area.area_id for area in chain(*transition_infos))
ALL_POSSIBLE_TRANSITIONS = tuple([
    (area.area_id, exit_.area_id)
    for area in TRANSITION_INFOS_DICT.values()
    for exit_ in area.exits
])


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

# Including the version number seems overkill,
# I don't think there was ever a non v0. Can add later if needed.
if GAME_VERSION != 0:
    raise Exception(f"Unknown game version {GAME_VERSION}!")
_addresses_map = {
    "GPH": {
        "D": Addresses(
            version_string="GC DE 0-00",
            previous_area_blocks_ptr=TODO,
            current_area=0x80417F50,
            area_load_state=TODO,
            player_ptr=TODO,
            item_swap=0x804C7734,
            shaman_shop_struct=TODO,
            backpack_struct=TODO,
        ),
        "E": Addresses(
            version_string="GC US 0-00",
            previous_area_blocks_ptr=0x80425788,
            current_area=0x8041BEB4,
            area_load_state=0x8041BEC8,
            player_ptr=0x8041BE4C,
            item_swap=0x804CB694,
            shaman_shop_struct=0x7E00955C,
            backpack_struct=0x8041A248,
        ),
        "F": Addresses(
            version_string="GC FR 0-00",
            previous_area_blocks_ptr=TODO,
            current_area=0x80417F30,
            area_load_state=TODO,
            player_ptr=0x80417EC8,
            item_swap=0x804C7714,
            shaman_shop_struct=TODO,
            backpack_struct=TODO,
        ),
        "P": Addresses(
            version_string="GC EU 0-00",
            previous_area_blocks_ptr=TODO,
            current_area=0x80417F10,
            area_load_state=TODO,
            player_ptr=TODO,
            item_swap=0x804C76F4,
            shaman_shop_struct=TODO,
            backpack_struct=TODO,
        ),
    },
    "RPF": {
        "E": Addresses(
            version_string="Wii US 0-00",
            previous_area_blocks_ptr=0x804542DC,
            current_area=0x80448D04,
            area_load_state=TODO,
            player_ptr=TODO,
            item_swap=0x80446608,
            shaman_shop_struct=TODO,
            backpack_struct=TODO,
        ),
        "P": Addresses(
            version_string="Wii EU 0-00",
            previous_area_blocks_ptr=0x804546DC,
            current_area=0x80449104,
            area_load_state=TODO,
            player_ptr=TODO,
            item_swap=0x80446A08,
            shaman_shop_struct=TODO,
            backpack_struct=TODO,
        ),
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


GC_MIN_ADDRESS = 0x80000000
GC_MEM_SIZE = 0x1800000
GC_MAX_ADDRESS = 0x80000000 + GC_MEM_SIZE - 1  # so 0x817FFFFF


class LevelCRC(IntEnum):
    ABANDONED_CAVERN = 0xEA667977
    ALTAR_OF_AGES = 0xABD7CCD8
    ALTAR_OF_HUITACA = 0x70EBFCA3
    APU_ILLAPU_SHRINE = 0x5511C46C
    BATTERED_BRIDGE = 0x69F0CDE2
    BETA_VOLCANO = 0x47508760
    BITTENBINDERS_CAMP = 0x0EF63551
    BUTTERFLY_GLADE = 0xCD944049
    CAVERN_LAKE = 0x8B372E42
    CHAMELEON_TEMPLE = 0x0081082C
    COPACANTI_LAKE = 0x8147EA91
    CRASH_SITE = 0xEE8F6900
    CRYSTAL_CAVERN = 0x0DDE5470
    EKKEKO_ICE_CAVERN = 0x3E7EE822
    EYES_OF_DOOM = 0x9A0C8DF8
    FIRE_BOMBED_TOWERS = 0xF0F99C58
    FLOODED_CAVE = 0x3A811024
    FLOODED_COURTYARD = 0xECC9D759
    GATES_OF_EL_DORADO = 0x93F89D45
    GREAT_TREE = 0x3292B6C9
    JAGUAR = 0x99885996
    JUNGLE_CANYON = 0xDEDA69BC
    JUNGLE_TRAIL = 0x7A9B3870
    KABOOM = 0xE411440A
    LADDER_OF_MILES = 0x619E1126
    MAIN_MENU = 0x00000000
    MAMA_OULLO_TOWER = 0x07ECCC35
    MONKEY_SPIRIT = 0x02C7B675
    MONKEY_TEMPLE = 0xF3B4DC8E
    MOUNTAIN_OVERLOOK = 0x907C492B
    MOUNTAIN_SLED_RUN = 0x1B8833D3
    MOUTH_OF_INTI = 0xB8D5CE86
    MYSTERIOUS_TEMPLE = 0x099BF148
    NATIVE_JUNGLE = 0x0AF1CCFF
    NATIVE_VILLAGE = 0x05AA726C
    PENGUIN_DEN = 0x1553BBE1
    PENGUIN_SPIRIT = 0x1F237F32
    PENGUIN_TEMPLE = 0x1B11EC74
    PICKAXE_RACE = 0x7A75D1A9
    PLANE_COCKPIT = 0x4A3E4058
    PLANE_CUTSCENE = 0x53257119
    PUNCHAU_SHRINE = 0x38C7AE7D
    PUSCA = 0xCFD2FE10
    RAFT_BOWLING = 0x9316749C
    RENEGADE_FORT = 0x0C1C3E47
    RENEGADE_HEADQUARTERS = 0x1CB1432D
    SCORPION_SPIRIT = 0x0305DC42
    SCORPION_TEMPLE = 0x4B08BBEB
    SPINJA_LAIR = 0x7652BAFC
    ST_CLAIRE_DAY = 0xBA9370DF
    ST_CLAIRE_NIGHT = 0x72AD42FA
    STATUES_OF_AYAR = 0xA85A2793
    TELEPORTS = 0xE97CB47C
    TUCO_SHOOT = 0x0D72E13F
    TURTLE_MONUMENT = 0x239A2165
    TWIN_OUTPOSTS = 0xE6B9138A
    TWIN_OUTPOSTS_UNDERWATER = 0xDE524DA6
    UNDERGROUND_DAM = 0x9D6149E1
    VALLEY_OF_SPIRITS = 0x08E3C641
    VIRACOCHA_MONOLITHS = 0x6F498BBD
    VIRACOCHA_MONOLITHS_CUTSCENE = 0xE8362F5F
    WHACK_A_TUCO = 0x0A1F2526
    WHITE_VALLEY = 0x62548B77


TEMPLES_WITH_FIGHT = {
    LevelCRC.MONKEY_TEMPLE: LevelCRC.MONKEY_SPIRIT,
    LevelCRC.SCORPION_TEMPLE: LevelCRC.SCORPION_SPIRIT,
    LevelCRC.PENGUIN_TEMPLE: LevelCRC.PENGUIN_SPIRIT,
}

SOFTLOCKABLE_ENTRANCES = {
    int(LevelCRC.FLOODED_COURTYARD): 8,  # From st claire: 7
    int(LevelCRC.EYES_OF_DOOM): 9,
    int(LevelCRC.VALLEY_OF_SPIRITS): 8,
    int(LevelCRC.COPACANTI_LAKE): 8,
}
"""Entrances that can softlock by infinitely running into a door.
Value is the minimum height boost needed to regain control."""
