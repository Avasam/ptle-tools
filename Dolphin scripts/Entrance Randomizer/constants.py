from __future__ import annotations

from itertools import chain

from transition_infos import transition_infos
from dolphin import memory  # pyright: ignore[reportMissingModuleSource]

DRAW_TEXT_STEP = 24
DRAW_TEXT_OFFSET_X = 272

TRANSITION_INFOS_DICT = {area.area_id: area for area in chain(*transition_infos)}
ALL_TRANSITION_AREAS = {area.area_id for area in chain(*transition_infos)}
ALL_POSSIBLE_EXITS = [exit_.area_id for exit_ in chain(*(area.exits for area in TRANSITION_INFOS_DICT.values()))]

_game_id = ''.join([chr(memory.read_u8(0x80000001+i)) for i in range(2)])
_developer_id = ''.join([chr(memory.read_u8(0x80000004+i)) for i in range(2)])
GAME_REGION = chr(memory.read_u8(0x80000003))
GAME_VERSION = memory.read_u8(0x80000007)
IS_GC = chr(memory.read_u8(0x80000000)) == 'G'
IS_WII = chr(memory.read_u8(0x80000000)) == 'R'

if IS_GC:
    if _game_id == 'PH' and _developer_id == '52':
        if GAME_REGION == 'E':
            if GAME_VERSION == 0:
                CURRENT_AREA_ADDR = 0x8041BEB4
                ITEM_SWAP_ADDR = 0x804CB694
                print("Detected US 0-00 version!")
            else:
                raise Exception(f'Unknown version of Pitfall The Lost Expedition (region -> {GAME_REGION}, version -> {GAME_VERSION})')
        elif GAME_REGION == 'F':
            if GAME_VERSION == 0:
                CURRENT_AREA_ADDR = 0x80417F30
                ITEM_SWAP_ADDR = 0x804C7714
                print("Detected FR 0-00 version!")
            else:
                raise Exception(f'Unknown version of Pitfall The Lost Expedition (region -> {GAME_REGION}, version -> {GAME_VERSION})')
        else:
            raise Exception(f'Unknown version of Pitfall The Lost Expedition (region -> {GAME_REGION}, version -> {GAME_VERSION})')
    else:
        raise Exception(f'Unknown game!')
elif IS_WII:
    if _game_id == 'PF' and _developer_id == '52':
        raise Exception('Wii version is not supported yet!')
    else:
        raise Exception(f'Unknown game!')
else:
    raise Exception(f'Unknown game!')


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
