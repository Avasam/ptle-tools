# https://github.com/Felk/dolphin/tree/scripting-preview2

from __future__ import annotations

import os
import sys
from pathlib import Path

from dolphin import event, memory  # pyright: ignore[reportMissingModuleSource]

dolphin_path = Path().absolute()
print("Dolphin path:", dolphin_path)
real_scripts_path = os.path.realpath(dolphin_path / "Scripts")
print("Real Scripts path:", real_scripts_path)
sys.path.append(f"{real_scripts_path}/Entrance Randomizer")
# Wait for the first frame before scanning the game for constants
await event.frameadvance()  # noqa: F704, PLE1142  # pyright: ignore

import CONFIGS
from lib.constants import *  # noqa: F403
from lib.constants import __version__
from lib.entrance_rando import (
    highjack_transition,
    highjack_transition_rando,
    set_transitions_map,
    starting_area,
    state,
    transitions_map,
)
from lib.shaman_shop import patch_shaman_shop, randomize_shaman_shop
from lib.utils import draw_text, dump_spoiler_logs, reset_draw_text_index

set_transitions_map()
randomize_shaman_shop()

# This is necessary until/unless I map all areas even those not randomized.
try:
    starting_area_name = TRANSITION_INFOS_DICT[starting_area].name
except KeyError:
    if starting_area == CRASH_SITE:
        starting_area_name = "Crash Site"
    elif starting_area == TELEPORTERS:
        starting_area_name = "Teleport"
    else:
        starting_area_name = str(starting_area)

# Dump spoiler logs
dump_spoiler_logs(starting_area_name, transitions_map, seed_string)


async def main_loop():
    # Read memory, setup loop values, print debug to screen
    reset_draw_text_index()
    state.current_area_old = state.current_area_new
    await event.frameadvance()
    state.current_area_new = memory.read_u32(ADDRESSES.current_area)
    current_area = TRANSITION_INFOS_DICT.get(state.current_area_new)
    draw_text(f"Rando version: {__version__}")
    draw_text(f"Seed: {seed_string}")
    draw_text(patch_shaman_shop())
    draw_text(
        f"Starting area: {hex(starting_area)}"
        + " (Random)" if CONFIGS.STARTING_AREA is None else f"{starting_area_name}",
    )
    draw_text(
        f"Current area: {hex(state.current_area_new).upper()}"
        + f"({current_area.name})" if current_area else "",
    )

    # Always re-enable Item Swap.
    if memory.read_u32(ADDRESSES.item_swap) == 1:
        memory.write_u32(ADDRESSES.item_swap, 0)

    # Skip the intro fight and cutscene
    if highjack_transition(0x0, JAGUAR, starting_area):
        return

    # Standardize the Altar of Ages exit
    if highjack_transition(ALTAR_OF_AGES, None, MYSTERIOUS_TEMPLE):
        # Even if the cutscene isn't actually watched.
        # Just leaving the Altar is good enough for the rando.
        state.visited_altar_of_ages = True
        state.current_area_new = MYSTERIOUS_TEMPLE

    # Standardize the Viracocha Monoliths cutscene
    if highjack_transition(None, VIRACOCHA_MONOLITHS_CUTSCENE, VIRACOCHA_MONOLITHS):
        state.current_area_new = VIRACOCHA_MONOLITHS

    # Standardize St. Claire's Excavation Camp
    if highjack_transition(None, ST_CLAIRE_NIGHT, ST_CLAIRE_DAY):
        state.current_area_new = ST_CLAIRE_DAY

    redirect = highjack_transition_rando()
    if redirect:
        state.current_area_new = redirect


while True:
    await main_loop()  # noqa: F704, PLE1142  # pyright: ignore
