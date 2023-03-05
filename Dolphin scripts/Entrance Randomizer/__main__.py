# https://github.com/Felk/dolphin/tree/scripting-preview2

# pylint: disable=await-outside-async,undefined-variable,global-statement
from __future__ import annotations

import os
import pathlib
import random
import sys

import CONFIGS
from constants import *  # pylint: disable=unused-wildcard-import,wildcard-import
from dolphin import event  # pyright: ignore[reportMissingModuleSource]
from dolphin import gui, memory  # pyright: ignore[reportMissingModuleSource]

dolphin_path = pathlib.Path().absolute()
print("Dolphin path:", dolphin_path)
real_scripts_path = os.path.realpath(dolphin_path / "Scripts")
print("Real Scripts path:", real_scripts_path)
sys.path.append(f"{real_scripts_path}/Entrance Randomizer")


# Sets the seed
seed = CONFIGS.SEED if CONFIGS.SEED else random.randrange(sys.maxsize)
random.seed(seed)
seed_string = hex(seed).upper() if isinstance(seed, int) else seed
print("Seed set to:", seed_string)


starting_area = (
    CONFIGS.STARTING_AREA
    if CONFIGS.STARTING_AREA
    else ALL_TRANSITION_AREAS[random.randrange(len(ALL_TRANSITION_AREAS))]
)

# Initialize a few values to be used in loop
current_area_old = 0
"""Area ID of teh previous frame"""
current_area_new = 0
"""Area ID of the current frame"""
draw_text_index = 0
"""Count how many times draw_text has been called this frame"""
justOverwrote = False
"""Prevent the rando from trigerring on its own change"""


# A hacky first demo, total chaos! (but seeded)
def highjack_transition_chaos():
    if (
        current_area_old != current_area_new
        and current_area_old in ALL_TRANSITION_AREAS
        and current_area_new in ALL_TRANSITION_AREAS
    ):
        possible_redirections = [
            area
            for area in ALL_TRANSITION_AREAS
            # Prevent looping on itself
            if area != current_area_old
            # Prevent unintended entrances to Crash Site (resets most progression!)
            and (
                area != CRASH_SITE
                # Going from Cockpit or Canyon to Crash Site is OK.
                or (
                    current_area_old in {PLANE_COCKPIT, JUNGLE_CANYON}
                    and current_area_new == CRASH_SITE
                )
            )
        ]

        random.seed(f"{current_area_old}{current_area_new}{seed}")
        redirect = possible_redirections[random.randrange(len(possible_redirections))]
        print(
            "highjack_transition_chaos |",
            f"From: {hex(current_area_old)},",
            f"To: {hex(current_area_new)}.",
            f"Redirecting to: {hex(redirect)}",
        )
        memory.write_u32(CURRENT_AREA_ADDR, redirect)
        return True
    return False


def highjack_transition(from_: int, to: int, redirect: int):
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


while True:
    # Read memory, setup loop values, print debug to screen
    draw_text_index = 0
    current_area_old = current_area_new
    await event.frameadvance()  # pyright: ignore
    current_area_new = memory.read_u32(CURRENT_AREA_ADDR)
    draw_text(f"Current area: {hex(current_area_new).upper()} ({TRANSITION_INFOS_DICT[current_area_new].name})")
    draw_text(f"Seed: {seed_string}")

    # Always re-enable Item Swap.
    if memory.read_u32(ITEM_SWAP_ADDR) == 1:
        memory.write_u32(ITEM_SWAP_ADDR, 0)

    # Skip the intro fight and cutscene
    if highjack_transition(0x0, JAGUAR, starting_area):
        continue

    # Standardize the Viracocha Monoliths cutscene
    if highjack_transition(
        current_area_old,
        VIRACOCHA_MONOLITHS_CUTSCENE,
        VIRACOCHA_MONOLITHS,
    ):
        current_area_new = VIRACOCHA_MONOLITHS

    if justOverwrote:
        justOverwrote = False
    elif highjack_transition_chaos():
        justOverwrote = True
