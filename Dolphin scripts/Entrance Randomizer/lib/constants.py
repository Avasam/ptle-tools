from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from enum import IntEnum
from itertools import chain

import CONFIGS
from dolphin import memory  # pyright: ignore[reportMissingModuleSource]
from lib.transition_infos import transition_infos

__version__ = "0.4.01"
"""
Major: New major feature or functionality

Minor: Affects seed

Patch: Does't affect seed (assuming same settings)
"""
print(f"Python version: {sys.version}")
print(f"Rando version: {__version__}")

# Sets the seed
seed = CONFIGS.SEED or random.randrange(sys.maxsize)
random.seed(seed)
seed_string = hex(seed).upper() if isinstance(seed, int) else seed
print("Seed set to:", seed_string)


@dataclass
class Addresses:
    version_string: str
    prev_area: list[int]
    current_area: int
    area_load_state: int
    player_x: list[int]
    player_y: list[int]
    player_z: list[int]
    item_swap: int
    shaman_shop_struct: int


TRANSITION_INFOS_DICT = {
    area.area_id: area for area in chain(*transition_infos)
}
ALL_TRANSITION_AREAS = {area.area_id for area in chain(*transition_infos)}
ALL_POSSIBLE_TRANSITIONS = [
    (area.area_id, exit_.area_id)
    for area in TRANSITION_INFOS_DICT.values()
    for exit_ in area.exits
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

# Including the version number seems overkill,
# I don't think there was ever a non v0. Can add later if needed.
if GAME_VERSION != 0:
    raise Exception(f"Unknown game version {GAME_VERSION}!")
_addresses_map = {
    "GPH": {
        "D": Addresses(
            version_string="GC DE 0-00",
            prev_area=[0x80747648],
            current_area=0x80417F50,
            area_load_state=TODO,
            player_x=[],
            player_y=[],
            player_z=[],
            item_swap=0x804C7734,
            shaman_shop_struct=TODO,
        ),
        "E": Addresses(
            version_string="GC US 0-00",
            prev_area=[0x8072B648],
            current_area=0x8041BEB4,
            area_load_state=0x8041BEC8,
            player_x=[0x8041BE4C, 0x338],
            player_y=[0x8041BE4C, 0x33C],
            player_z=[0x8041BE4C, 0x340],
            item_swap=0x804CB694,
            shaman_shop_struct=0x7E00955C,
        ),
        "F": Addresses(
            version_string="GC FR 0-00",
            prev_area=[0x80747648],
            current_area=0x80417F30,
            area_load_state=TODO,
            player_x=[],
            player_y=[],
            player_z=[],
            item_swap=0x804C7714,
            shaman_shop_struct=TODO,
        ),
        "P": Addresses(
            version_string="GC EU 0-00",
            prev_area=[0x80747648],
            current_area=0x80417F10,
            area_load_state=TODO,
            player_x=[],
            player_y=[],
            player_z=[],
            item_swap=0x804C76F4,
            shaman_shop_struct=TODO,
        ),
    },
    "RPF": {
        "E": Addresses(
            version_string="Wii US 0-00",
            prev_area=[0x804542DC, 0x8],
            current_area=0x80448D04,
            area_load_state=TODO,
            player_x=[],
            player_y=[],
            player_z=[],
            item_swap=0x80446608,
            shaman_shop_struct=TODO,
        ),
        "P": Addresses(
            version_string="Wii EU 0-00",
            prev_area=[0x804546DC, 0x18],
            current_area=0x80449104,
            area_load_state=TODO,
            player_x=[],
            player_y=[],
            player_z=[],
            item_swap=0x80446A08,
            shaman_shop_struct=TODO,
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


class LevelCRC(IntEnum):
    JAGUAR = 0x99885996
    CRASH_SITE = 0xEE8F6900
    PLANE_COCKPIT = 0x4A3E4058
    JUNGLE_CANYON = 0xDEDA69BC
    CHAMELEON_TEMPLE = 0x0081082C
    BITTENBINDERS_CAMP = 0x0EF63551
    MYSTERIOUS_TEMPLE = 0x099BF148
    ALTAR_OF_AGES = 0xABD7CCD8
    MOUTH_OF_INTI = 0xB8D5CE86
    MAMA_OULLO_TOWER = 0x07ECCC35
    FLOODED_COURTYARD = 0xECC9D759
    TURTLE_MONUMENT = 0x239A2165
    NATIVE_VILLAGE = 0x05AA726C
    RENEGADE_HEADQUARTERS = 0x1CB1432D
    EYES_OF_DOOM = 0x9A0C8DF8
    SCORPION_TEMPLE = 0x4B08BBEB
    MOUNTAIN_OVERLOOK = 0x907C492B
    WHITE_VALLEY = 0x62548B77
    CAVERN_LAKE = 0x8B372E42
    VIRACOCHA_MONOLITHS = 0x6F498BBD
    VIRACOCHA_MONOLITHS_CUTSCENE = 0xE8362F5F
    PENGUIN_TEMPLE = 0x1B11EC74
    VALLEY_OF_THE_SPIRITS = 0x08E3C641
    COPACANTI_LAKE = 0x8147EA91
    MOUNTAIN_SLED_RUN = 0x1B8833D3
    APU_ILLAPU_SHRINE = 0x5511C46C
    ST_CLAIRE_DAY = 0xBA9370DF
    ST_CLAIRE_NIGHT = 0x72AD42FA
    GATES_OF_EL_DORADO = 0x93F89D45
    TELEPORTS = 0xE97CB47C


SOFTLOCKABLE_ENTRANCES = {
    int(LevelCRC.FLOODED_COURTYARD): 8,  # From st claire: 7
    int(LevelCRC.EYES_OF_DOOM): 9,
    int(LevelCRC.VALLEY_OF_THE_SPIRITS): 8,
    int(LevelCRC.COPACANTI_LAKE): 8,
}
"""Entrances that can softlock by infinitly running into a door.
Value is the minimum height boost needed to regain control."""

GC_MIN_ADDRESS = 0x80000000
GC_MEM_SIZE = 0x1800000
GC_MAX_ADDRESS = 0x80000000 + GC_MEM_SIZE - 1  # so 0x817FFFFF
