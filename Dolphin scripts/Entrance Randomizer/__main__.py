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
    transitions_map,
)
from lib.shaman_shop import patch_shaman_shop, randomize_shaman_shop
from lib.utils import (
    create_graphml,
    draw_text,
    dump_spoiler_logs,
    follow_pointer_path,
    prevent_transition_softlocks,
    reset_draw_text_index,
    state,
)

set_transitions_map()
randomize_shaman_shop()

# Create .graphml file
create_graphml(transitions_map, seed_string, starting_area)

# This is necessary until/unless I map all areas even those not randomized.
try:
    starting_area_name = TRANSITION_INFOS_DICT[starting_area].name
except KeyError:
    starting_area_name = hex(starting_area).upper() + " (not in randomization)"

# Dump spoiler logs
dump_spoiler_logs(starting_area_name, transitions_map, seed_string)


async def main_loop():
    # Read memory, setup loop values, print debug to screen
    reset_draw_text_index()
    state.current_area_old = state.current_area_new
    state.area_load_state_old = state.area_load_state_new
    await event.frameadvance()
    state.current_area_new = memory.read_u32(ADDRESSES.current_area)
    state.area_load_state_new = memory.read_u32(ADDRESSES.area_load_state)
    current_area = TRANSITION_INFOS_DICT.get(state.current_area_new)
    previous_area_id = memory.read_u32(follow_pointer_path(ADDRESSES.prev_area))
    previous_area = TRANSITION_INFOS_DICT.get(previous_area_id)
    draw_text(f"Rando version: {__version__}")
    draw_text(f"Seed: {seed_string}")
    draw_text(patch_shaman_shop())
    draw_text(
        f"Starting area: {hex(starting_area).upper()} (Random)" if CONFIGS.STARTING_AREA is None
        else f"Starting area: {starting_area_name}",
    )
    draw_text(
        f"Current area: {hex(state.current_area_new).upper()} "
        + (f"({current_area.name})" if current_area else ""),
    )
    draw_text(
        f"From entrance: {hex(previous_area_id).upper()} "
        + (f"({previous_area.name})" if previous_area else ""),
    )

    # Always re-enable Item Swap.
    if memory.read_u32(ADDRESSES.item_swap) == 1:
        memory.write_u32(ADDRESSES.item_swap, 0)

    # Skip the intro fight and cutscene
    """
    This is disabled because we want to fight Jaguar 2 at the end of the game. So we need to fight Jaguar 1 at the start.
    If we fight Jaguar 1 at any other time it will result in us losing all our items and abilities, which sucks.
    Instead we just hijack Jaguar -> Plane Crash CUTSCENE to send us to starting_area
    """
    # if highjack_transition(0x0, LevelCRC.JAGUAR, starting_area):
    #     return

    # Standardize the Altar of Ages exit to remove the Altar -> BBCamp transition
    if highjack_transition(
            LevelCRC.ALTAR_OF_AGES,
            LevelCRC.BITTENBINDERS_CAMP,
            LevelCRC.MYSTERIOUS_TEMPLE,
    ):
        state.current_area_new = LevelCRC.MYSTERIOUS_TEMPLE
        # Even if the cutscene isn't actually watched.
        # Just leaving the Altar is good enough for the rando.
        state.visited_altar_of_ages = True

    # Standardize the Viracocha Monoliths cutscene
    if highjack_transition(
            None,
            LevelCRC.VIRACOCHA_MONOLITHS_CUTSCENE,
            LevelCRC.VIRACOCHA_MONOLITHS,
    ):
        state.current_area_new = LevelCRC.VIRACOCHA_MONOLITHS

    # Standardize St. Claire's Excavation Camp
    if highjack_transition(None, LevelCRC.ST_CLAIRE_NIGHT, LevelCRC.ST_CLAIRE_DAY):
        state.current_area_new = LevelCRC.ST_CLAIRE_DAY

    # TODO: Skip swim levels (3)

    redirect = highjack_transition_rando()
    if redirect:
        state.current_area_new = redirect[1]

    prevent_transition_softlocks()


while True:
    await main_loop()  # noqa: F704, PLE1142  # pyright: ignore
