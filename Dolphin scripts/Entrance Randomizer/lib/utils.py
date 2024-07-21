from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import ClassVar

from dolphin import gui  # pyright: ignore[reportMissingModuleSource]
from lib.constants import *  # noqa: F403
from lib.constants import __version__
from lib.entrance_rando import (
    _transition_infos_dict_rando,
    bypassed_exits,
    disabled_exits,
)
from lib.types_ import SeedType

DRAW_TEXT_STEP = 24
DRAW_TEXT_OFFSET_X = 272
_draw_text_index = 0
"""Count how many times draw_text has been called this frame"""


@dataclass
class State:
    # Initialize a few values to be used in loop
    area_load_state_old = 0
    area_load_state_new = 0
    current_area_old = 0
    """Area ID of the previous frame"""
    current_area_new = 0
    """Area ID of the current frame"""
    visited_levels: ClassVar[set[int]] = set()
    no_connection_found_error = False
    """Whether the algorithm fails to find a valid connection to break open."""


state = State()


def reset_draw_text_index():
    global _draw_text_index
    _draw_text_index = 0


def draw_text(text: str):
    global _draw_text_index
    gui.draw_text(
        (DRAW_TEXT_OFFSET_X, DRAW_TEXT_STEP / 2 + DRAW_TEXT_STEP * _draw_text_index),
        0xFF00FFFF,
        text,
    )
    _draw_text_index += 1


def follow_pointer_path(ppath: Sequence[int]):
    addr = ppath[0]
    for i in range(len(ppath) - 1):
        addr = memory.read_u32(addr) + ppath[i + 1]
        if addr < GC_MIN_ADDRESS or addr > GC_MAX_ADDRESS:
            raise ValueError(
                f"Invalid address {hex(addr).upper()} for pointer path "
                + str([hex(level).upper() for level in ppath]),
            )
    return addr


def highjack_transition(
    from_: int | None,
    to: int | None,
    redirect: int,
):
    if from_ is None:
        from_ = state.current_area_old
    if to is None:
        to = state.current_area_new

    # Early return. Detect the start of a transition
    if state.current_area_old == state.current_area_new:
        return False

    if from_ == state.current_area_old and to == state.current_area_new:
        print(
            "highjack_transition |",
            f"From: {hex(state.current_area_old)},",
            f"To: {hex(state.current_area_new)}.",
            f"Redirecting to: {hex(redirect)}",
        )
        memory.write_u32(ADDRESSES.current_area, redirect)
        state.current_area_new = redirect
        return True
    return False


def prevent_transition_softlocks():
    """Prevents softlocking on closed doors by making Harry land."""
    height_offset = SOFTLOCKABLE_ENTRANCES.get(state.current_area_new)
    if (
        # As far as we're concerned, these are indeed magic numbers.
        # We haven't identified a name for these states yet.
        state.area_load_state_old == 5 and state.area_load_state_new == 6  # noqa: PLR2004
        # TODO: Include "from" transition to only bump player up when needed
        and height_offset
    ):
        player_z_addr = follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.PositionZ))
        memory.write_f32(player_z_addr, memory.read_f32(player_z_addr) + height_offset)


def prevent_item_softlock():
    """
    Prevent softlocking by missing the right items.

    Even with logic this can happen if the player bypasses logic.
    """
    # TODO: A better fix would be to just teleport the player to the entrance of the temple,
    # but we can't reliably do that yet.
    # And we can't use position-based fix as the game checks for walls even when teleporting

    # Pickaxe lets you escape everything
    if memory.read_u32(ADDRESSES.backpack_struct + BackpackOffset.Pickaxes):
        return

    # Scorpion Temple
    if (
        state.area_load_state_new == 5  # noqa: PLR2004
        and state.current_area_new == LevelCRC.SCORPION_TEMPLE
        and -1 < memory.read_f32(
            follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.PositionX)),
        ) < 1
        and -1 < memory.read_f32(
            follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.PositionY)),
        ) < 1
    ):
        # Lets just give the player the torch, it's not like it unlocks much outside convenience.
        # TODO: Remove Scorpion Temple from UPGRADE_AREAS once we don't give the torch anymore
        memory.write_u32(ADDRESSES.backpack_struct + BackpackOffset.Torch, 1)
        return

    # Penguin Temple: https://youtu.be/LHglikRqeAw

    # Apu Illapu Shrine
    if (
        state.area_load_state_new == 6  # noqa: PLR2004, PLR0916
        and state.current_area_new == LevelCRC.APU_ILLAPU_SHRINE
        # Pickaxe (already checked), TNT and Breakdance are an easy out
        and not memory.read_u32(ADDRESSES.backpack_struct + BackpackOffset.TNT)
        and not memory.read_u32(
            follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.Breakdance)),
        )
        # Super sling check
        and not (
            memory.read_u32(follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.SuperSling)))
            and memory.read_u32(ADDRESSES.backpack_struct + BackpackOffset.Slingshot)
        )
        # Item sliding check
        and not (
            memory.read_u32(
                follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.HeroicDash)),
            ) and any(
                memory.read_u32(ADDRESSES.backpack_struct + item)
                for item in (
                    BackpackOffset.Canteen,
                    BackpackOffset.Slingshot,
                    BackpackOffset.Torch,
                    BackpackOffset.Shield,
                    BackpackOffset.GasMask,
                    BackpackOffset.TNT,
                )
            )
        )
    ):
        draw_text("Missing requirements to complete Apu Illapu Shrine. Kicking you out!")
        memory.write_u32(
            follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.CollideState)),
            0,
        )
        memory.write_f32(
            follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.PositionX)),
            -24,
        )
        memory.write_f32(
            follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.PositionY)),
            38,
        )
        memory.write_f32(
            follow_pointer_path((ADDRESSES.player_ptr, PlayerPtrOffset.PositionZ)),
            20,
        )
        return


def dump_spoiler_logs(
    starting_area_name: str,
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    seed_string: SeedType,
):
    spoiler_logs = f"Starting area: {starting_area_name}\n"
    red_string_list = [
        f"{_transition_infos_dict_rando[original[0]].name} "
        + f"({_transition_infos_dict_rando[original[1]].name} exit) "
        + f"will redirect to: {_transition_infos_dict_rando[redirect[1]].name} "
        + f"({_transition_infos_dict_rando[redirect[0]].name} entrance)\n"
        for original, redirect in transitions_map.items()
    ]
    red_string_list.sort()
    for string in red_string_list:
        spoiler_logs += string

    spoiler_logs += "\nUnrandomized transitions:\n"
    non_random_string_list = [
        f"From: {TRANSITION_INFOS_DICT[pair[0]].name}, "
        + f"To: {TRANSITION_INFOS_DICT[pair[1]].name}.\n"
        for pair in disabled_exits if pair not in bypassed_exits
    ]
    non_random_string_list.sort()
    for string in non_random_string_list:
        spoiler_logs += string

    # TODO (Avasam): Get actual user folder based whether Dolphin Emulator is in AppData/Roaming
    # and if the current installation is portable.
    dolphin_path = Path().absolute()
    spoiler_logs_file = (
        dolphin_path
        / "User"
        / "Logs"
        / f"SPOILER_LOGS_v{__version__}_{seed_string}.txt"
    )
    Path.mkdir(spoiler_logs_file.parent, parents=True, exist_ok=True)
    Path.write_text(spoiler_logs_file, spoiler_logs)
    print("Spoiler logs written to", spoiler_logs_file)
