# https://github.com/Felk/dolphin/tree/scripting-preview2

from __future__ import annotations

import os
import random
import sys
from pathlib import Path
from typing import Iterable

from dolphin import event, gui, memory  # pyright: ignore[reportMissingModuleSource]

print(f"Python version: {sys.version}")
dolphin_path = Path().absolute()
print("Dolphin path:", dolphin_path)
real_scripts_path = os.path.realpath(dolphin_path / "Scripts")
print("Real Scripts path:", real_scripts_path)
sys.path.append(f"{real_scripts_path}/Entrance Randomizer")

import CONFIGS
from constants import *  # noqa: F403

__version__ = "0.3"
"""
Major: New major feature or functionality

Minor: Affects seed

Patch: Does't affect seed (assuming same settings)
"""
print(f"Rando version: {__version__}")

# Sets the seed
seed = CONFIGS.SEED if CONFIGS.SEED else random.randrange(sys.maxsize)
random.seed(seed)
seed_string = hex(seed).upper() if isinstance(seed, int) else seed
print("Seed set to:", seed_string)

_possible_starting_areas = [
    area for area in ALL_TRANSITION_AREAS
    # Remove impossible start areas + Don't immediatly give TNT
    if area not in {APU_ILLAPU_SHRINE, SCORPION_TEMPLE, ST_CLAIRE_DAY}
    # Add back areas removed from transitions because of issues
] + [CRASH_SITE, TELEPORTERS]

starting_area = (
    CONFIGS.STARTING_AREA
    if CONFIGS.STARTING_AREA
    else random.choice(_possible_starting_areas)
)

# Initialize a few values to be used in loop
current_area_old = 0
"""Area ID of teh previous frame"""
current_area_new = 0
"""Area ID of the current frame"""
draw_text_index = 0
"""Count how many times draw_text has been called this frame"""
visited_altar_of_ages = False


def highjack_transition_rando():
    # Early reaturn, faster check
    if current_area_old == current_area_new:
        return False

    redirect = transitions_map.get(current_area_old, {}).get(current_area_new)
    if not redirect:
        return False

    # Apply Altar of Ages logic to St. Claire's Excavation Camp
    if redirect in {ST_CLAIRE_DAY, ST_CLAIRE_NIGHT}:
        redirect = ST_CLAIRE_NIGHT if visited_altar_of_ages else ST_CLAIRE_DAY

    print(
        "highjack_transition_rando |",
        f"From: {hex(current_area_old)},",
        f"To: {hex(current_area_new)}.",
        f"Redirecting to: {hex(redirect)}",
    )
    memory.write_u32(CURRENT_AREA_ADDR, redirect)
    return redirect


def highjack_transition(from_: int | None, to: int | None, redirect: int):
    if from_ is None:
        from_ = current_area_old
    if to is None:
        to = current_area_new
    if from_ == current_area_old and to == current_area_new:
        print(
            "highjack_transition |",
            f"From: {hex(current_area_old)},",
            f"To: {hex(current_area_new)}.",
            f"Redirecting to: {hex(redirect)}",
        )
        memory.write_u32(CURRENT_AREA_ADDR, redirect)
        return True
    return False


def draw_text(text: str):
    global draw_text_index
    gui.draw_text(
        (DRAW_TEXT_OFFSET_X, DRAW_TEXT_STEP / 2 + DRAW_TEXT_STEP * draw_text_index),
        0xFF00FFFF,
        text,
    )
    draw_text_index += 1


def get_random_redirection(from_: int, _original_to: int, possible_redirections: Iterable[int]):
    possible_redirections = [
        area for area in possible_redirections
        # Prevent looping on itself
        if area != from_
        # Prevent unintended entrances to Crash Site (resets most progression!)
        # and (
        #     area != CRASH_SITE
        #     # Going from Cockpit or Canyon to Crash Site is OK.
        #     or (
        #         from_ in {PLANE_COCKPIT, JUNGLE_CANYON}
        #         and original_to == CRASH_SITE
        #     )
        # )
    ]
    # Investigate and explain why that can happen
    return random.choice(possible_redirections) \
        if len(possible_redirections) > 0 \
        else None


transitions_map: dict[int, dict[int, int]] = {}
"""
{
    from_id: {
        og_to_id: remapped_to_id
    }
}
"""


def set_transitions_map():
    def _transition_map_set(from_: int, to: int, redirect: int):
        if transitions_map.get(from_):
            transitions_map[from_][to] = redirect
        else:
            transitions_map[from_] = {to: redirect}
    _possible_exits_bucket = ALL_POSSIBLE_EXITS.copy()
    """A temporary container of transitions to pick from until it is empty."""
    global transitions_map
    transitions_map = {}
    for area in TRANSITION_INFOS_DICT.values():
        from_ = area.area_id
        for to_og in (exit_.area_id for exit_ in area.exits):
            redirect = get_random_redirection(from_, to_og, _possible_exits_bucket)
            if redirect is None or transitions_map.get(from_, {}).get(to_og):
                # Don't override something set in a previous iteration, like from linked two-way entrances
                continue

            _transition_map_set(from_, to_og, redirect)
            _possible_exits_bucket.remove(redirect)

            if CONFIGS.LINKED_TRANSITIONS:
                # Ensure we haven't already expanded all transitions back to the "from" area.
                # (I think that means that area had more exits than entrances)
                if from_ not in _possible_exits_bucket:
                    continue
                try:
                    # Get a still-available exit from the area we're redirecting to
                    entrance = [
                        exit_.area_id for exit_
                        in TRANSITION_INFOS_DICT[redirect].exits
                        if exit_.area_id in _possible_exits_bucket
                    ][0]
                except IndexError:
                    # That area had more entrances than exits
                    continue
                _transition_map_set(redirect, entrance, from_)
                _possible_exits_bucket.remove(from_)


set_transitions_map()

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
spoiler_logs = f"Starting area: {starting_area_name}\n"
for from_, to_old_and_new in transitions_map.items():
    for to_old, to_new in to_old_and_new.items():
        spoiler_logs += f"From: {TRANSITION_INFOS_DICT[from_].name}, " + \
            f"To: {TRANSITION_INFOS_DICT[to_old].name}. " + \
            f"Redirecting to: {TRANSITION_INFOS_DICT[to_new].name}\n"

spoiler_logs_file = dolphin_path / "User" / "Logs" / f"SPOILER_LOGS_v{__version__}_{seed_string}.txt"
with Path.open(spoiler_logs_file, "w") as file:
    file.writelines(spoiler_logs)
print("Spoiler logs written to", spoiler_logs_file)


async def main_loop():
    global current_area_old
    global current_area_new
    global draw_text_index
    global visited_altar_of_ages

    # Read memory, setup loop values, print debug to screen
    draw_text_index = 0
    current_area_old = current_area_new
    await event.frameadvance()
    current_area_new = memory.read_u32(CURRENT_AREA_ADDR)
    current_area = TRANSITION_INFOS_DICT.get(current_area_new)
    draw_text(f"Rando version: {__version__}")
    draw_text(f"Seed: {seed_string}")
    draw_text(
        f"Starting area: {hex(starting_area)}"
        + " (Random)" if CONFIGS.STARTING_AREA is None else f"{starting_area_name}",
    )
    draw_text(f"Current area: {hex(current_area_new).upper()} {f'({current_area.name})' if current_area else ''}")

    # Always re-enable Item Swap.
    if memory.read_u32(ITEM_SWAP_ADDR) == 1:
        memory.write_u32(ITEM_SWAP_ADDR, 0)

    # Skip the intro fight and cutscene
    if highjack_transition(0x0, JAGUAR, starting_area):
        return

    # Standardize the Altar of Ages exit
    if highjack_transition(ALTAR_OF_AGES, None, MYSTERIOUS_TEMPLE):
        # Even if the cutscene isn't actually watched. Just leaving the Altar is good enough for the rando.
        visited_altar_of_ages = True
        current_area_new = MYSTERIOUS_TEMPLE

    # Standardize the Viracocha Monoliths cutscene
    if highjack_transition(None, VIRACOCHA_MONOLITHS_CUTSCENE, VIRACOCHA_MONOLITHS):
        current_area_new = VIRACOCHA_MONOLITHS

    # Standardize St. Claire's Excavation Camp
    if highjack_transition(None, ST_CLAIRE_NIGHT, ST_CLAIRE_DAY):
        current_area_new = ST_CLAIRE_DAY

    redirect = highjack_transition_rando()
    if redirect:
        current_area_new = redirect


while True:
    await main_loop()  # noqa: F704  # pyright: ignore
