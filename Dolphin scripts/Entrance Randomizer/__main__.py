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
    highjack_transition_rando,
    set_transitions_map,
    starting_area,
    temp_disabled_exits,
    transitions_map,
)
from lib.graph_creation import create_graphml
from lib.shaman_shop import patch_shaman_shop, randomize_shaman_shop
from lib.utils import (
    PreviousArea,
    draw_text,
    dump_spoiler_logs,
    follow_pointer_path,
    highjack_transition,
    prevent_item_softlock,
    prevent_transition_softlocks,
    reset_draw_text_index,
    state,
)

set_transitions_map()
randomize_shaman_shop()

# This is necessary as long as the player can choose an unused level (which isn't in the json)
try:
    starting_area_name = TRANSITION_INFOS_DICT[starting_area].name
except KeyError:
    starting_area_name = hex(starting_area).upper() + " (unknown level)"

# Dump spoiler logs and graph
dump_spoiler_logs(starting_area_name, transitions_map, seed_string)
create_graphml(transitions_map, temp_disabled_exits, seed_string, starting_area)


async def main_loop():
    # Read memory, setup loop values, print debug to screen
    reset_draw_text_index()
    state.current_area_old = state.current_area_new
    state.area_load_state_old = state.area_load_state_new
    await event.frameadvance()
    state.current_area_new = memory.read_u32(ADDRESSES.current_area)
    state.area_load_state_new = memory.read_u32(ADDRESSES.area_load_state)
    current_area = TRANSITION_INFOS_DICT.get(state.current_area_new)
    previous_area_id = PreviousArea.get()
    draw_text(f"Rando version: {__version__}")
    draw_text(f"Seed: {seed_string}")
    draw_text(patch_shaman_shop())
    draw_text(
        f"Current area: {hex(state.current_area_new).upper()} "
        + (f"({current_area.name})" if current_area else ""),
    )
    if previous_area_id != -1 or state.current_area_new in {starting_area, 0}:
        previous_area = TRANSITION_INFOS_DICT.get(previous_area_id)
        draw_text(
            f"From entrance: {hex(previous_area_id).upper()} "
            + (f"({previous_area.name})" if previous_area else ""),
        )
    else:
        draw_text(
            "From entrance: NOT FOUND!!!\n"
            + "This is either an entrance using a special ID we're not aware of, or a bug!\n"
            + "PLEASE REPORT THIS TO RANDO DEVS\n"
            + f"ID might be: {hex(memory.read_u32(PreviousArea._previous_area_address)).upper()}",  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
        )

    # Always re-enable Item Swap
    if memory.read_u32(ADDRESSES.item_swap) == 1:
        memory.write_u32(ADDRESSES.item_swap, 0)

    # Track the visited levels for different purposes.
    # We only consider a level "visited" once leaving it.
    state.visited_levels.add(state.current_area_old)

    # Skip both Jaguar fights if configured
    if CONFIGS.SKIP_JAGUAR:
        if highjack_transition(LevelCRC.MAIN_MENU, LevelCRC.JAGUAR, starting_area):
            return
        if highjack_transition(LevelCRC.GATES_OF_EL_DORADO, LevelCRC.JAGUAR, LevelCRC.PUSCA):
            return

    # Standardize the Altar of Ages exit to remove the Altar -> BBCamp transition
    highjack_transition(
        LevelCRC.ALTAR_OF_AGES,
        LevelCRC.BITTENBINDERS_CAMP,
        LevelCRC.MYSTERIOUS_TEMPLE,
    )

    # Standardize the Viracocha Monoliths cutscene
    highjack_transition(
        None,
        LevelCRC.VIRACOCHA_MONOLITHS_CUTSCENE,
        LevelCRC.VIRACOCHA_MONOLITHS,
    )

    # Standardize St. Claire's Excavation Camp
    highjack_transition(None, LevelCRC.ST_CLAIRE_NIGHT, LevelCRC.ST_CLAIRE_DAY)

    # TODO: Skip swim levels (3)

    highjack_transition_rando()

    prevent_item_softlock()
    prevent_transition_softlocks()


while True:
    await main_loop()  # noqa: F704, PLE1142  # pyright: ignore
