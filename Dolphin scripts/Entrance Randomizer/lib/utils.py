from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from dolphin import gui  # pyright: ignore[reportMissingModuleSource]
from lib.constants import *  # noqa: F403
from lib.constants import __version__
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
    visited_altar_of_ages = False


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


def dump_spoiler_logs(
    starting_area_name: str,
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    seed_string: SeedType,
):
    spoiler_logs = f"Starting area: {starting_area_name}\n"
    for original, redirect in transitions_map.items():
        spoiler_logs += (
            f"{TRANSITION_INFOS_DICT[original[0]].name} "
            + f"({TRANSITION_INFOS_DICT[original[1]].name} exit) "
            + f"will redirect to: {TRANSITION_INFOS_DICT[redirect[1]].name} "
            + f"({TRANSITION_INFOS_DICT[redirect[0]].name} entrance)\n"
        )

    # Currently this should not be possible, but maybe in the future this will play a part
    unrandomized_transitions = ALL_POSSIBLE_TRANSITIONS - transitions_map.keys()
    if len(unrandomized_transitions) > 0:
        spoiler_logs += "\nUnrandomized transitions:\n"
        for transition in unrandomized_transitions:
            spoiler_logs += (
                f"From: {TRANSITION_INFOS_DICT[transition[0]].name}, "
                + f"To: {TRANSITION_INFOS_DICT[transition[1]].name}.\n"
            )

    spoiler_logs += (
        "\nThe following levels are currently excluded from the randomization process:\n"
        + "- Scorpion Temple\n"
        + "- Mouth of Inti\n"
        + "- Twin Outposts (Underwater Passage)\n"
    )

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


def prevent_transition_softlocks():
    """Prevents softlocking on closed door by making Harry land."""
    # As far as we're concerned, these are indeed magic numbers.
    # We haven't identified a name for these states yet.
    height_offset = SOFTLOCKABLE_ENTRANCES.get(state.current_area_new)
    if (
        state.area_load_state_old == 5 and state.area_load_state_new == 6  # noqa: PLR2004
        # TODO: Include "from" transition to only bump player up when needed
        and height_offset
    ):
        player_z_addr = follow_pointer_path(ADDRESSES.player_z)
        # memory.write_f32(player_x_addr, memory.read_f32(player_x_addr) + 30)
        # memory.write_f32(player_y_addr, memory.read_f32(player_y_addr) + 30)
        memory.write_f32(player_z_addr, memory.read_f32(player_z_addr) + height_offset)
