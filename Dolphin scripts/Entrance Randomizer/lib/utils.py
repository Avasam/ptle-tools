from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import ClassVar, NamedTuple

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
    visited_levels: ClassVar[set[int]] = set()


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
    original_from: int | None,
    original_to: int | None,
    redirect_from: int,
    redirect_to: int,
):
    """
    Highjack a transition to transport the player elsewhere.

    `original_from=None` means that any entrance will match.
    `original_from=None` means that any exit will match.
    """
    if original_from is None:
        original_from = state.current_area_old
    if original_to is None:
        original_to = state.current_area_new

    # Early return. Detect the start of a transition
    if state.current_area_old == state.current_area_new:
        return False

    if original_from == state.current_area_old and original_to == state.current_area_new:
        print(
            "highjack_transition |",
            f"From: {hex(state.current_area_old)},",
            f"To: {hex(state.current_area_new)}.",
            f"Redirecting to: {hex(redirect_to)} ",
            f"from {hex(redirect_from)} entrance",
        )
        PreviousArea.set(Transition(redirect_from, redirect_to))
        memory.write_u32(ADDRESSES.current_area, redirect_to)
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


class Transition(NamedTuple):
    from_: int
    to: int


class PreviousArea:
    _previous_area_address = 0
    # TODO: This information is going to be extremely important for the transition rando,
    # we're gonna have to update out data structure to be able to make use of this.
    CORRECTED_TRANSITION_FROM: ClassVar[dict[Transition, int]] = {
        Transition(from_=LevelCRC.APU_ILLAPU_SHRINE, to=LevelCRC.WHITE_VALLEY): 0xF3ACDE92,
        # Probably a leftover from when plane crash + cockpit was a single map
        Transition(from_=LevelCRC.CRASH_SITE, to=LevelCRC.JUNGLE_CANYON): 0xD33711E2,
        # Scorpion/Explorer entrance
        # Transition(from_=LevelCRC.NATIVE_JUNGLE, to=LevelCRC.FLOODED_COURTYARD): 0x83A6748F,
        # HACK for CORRECTED_PREV_ID
        Transition(from_=LevelCRC.NATIVE_JUNGLE, to=0): 0x83A6748F,
        # Dark cave entrance
        Transition(from_=LevelCRC.NATIVE_JUNGLE, to=LevelCRC.FLOODED_COURTYARD): 0x1AAF2535,
        # Dark cave entrance
        Transition(from_=LevelCRC.FLOODED_COURTYARD, to=LevelCRC.NATIVE_JUNGLE): 0x402D3708,
        # Jungle Outpost well
        # Transition(from_=LevelCRC.TWIN_OUTPOSTS, to=LevelCRC.TWIN_OUTPOSTS_UNDERWATER): 0x9D1A6D4A,
        # HACK for CORRECTED_PREV_ID
        Transition(from_=LevelCRC.TWIN_OUTPOSTS, to=0): 0x9D1A6D4A,
        # Burning Outpost well
        Transition(from_=LevelCRC.TWIN_OUTPOSTS, to=LevelCRC.TWIN_OUTPOSTS_UNDERWATER): 0x7C65128A,
        # Jungle Outpost side
        # Transition(from_=LevelCRC.TWIN_OUTPOSTS_UNDERWATER, to=LevelCRC.TWIN_OUTPOSTS): 0x00D15464,
        # HACK for CORRECTED_PREV_ID
        Transition(from_=LevelCRC.TWIN_OUTPOSTS_UNDERWATER, to=0): 0x00D15464,
        # Burning Outpost side
        Transition(from_=LevelCRC.TWIN_OUTPOSTS_UNDERWATER, to=LevelCRC.TWIN_OUTPOSTS): 0xE1AE2BA4,
        # Native Village uses its own ID to spawn at the Native Games gate
        Transition(from_=LevelCRC.KABOOM, to=LevelCRC.NATIVE_VILLAGE): LevelCRC.NATIVE_VILLAGE,
        Transition(from_=LevelCRC.PICKAXE_RACE, to=LevelCRC.NATIVE_VILLAGE): LevelCRC.NATIVE_VILLAGE,  # noqa: E501
        Transition(from_=LevelCRC.RAFT_BOWLING, to=LevelCRC.NATIVE_VILLAGE): LevelCRC.NATIVE_VILLAGE,  # noqa: E501
        Transition(from_=LevelCRC.TUCO_SHOOT, to=LevelCRC.NATIVE_VILLAGE): LevelCRC.NATIVE_VILLAGE,
        Transition(from_=LevelCRC.WHACK_A_TUCO, to=LevelCRC.NATIVE_VILLAGE): LevelCRC.NATIVE_VILLAGE,  # noqa: E501
    }
    """
    Some entrances are mapped to a different ID than the level the player actually comes from.
    This maps the transition to the fake ID.
    """

    CORRECTED_PREV_ID: ClassVar[dict[int, int]] = {
        area_id: transition.from_
        for transition, area_id
        in CORRECTED_TRANSITION_FROM.items()
    }
    """
    Some entrances are mapped to a different ID than the level the player actually comes from.
    This maps the fake ID to the real ID.
    """
    __ALL_LEVELS = (
        ALL_TRANSITION_AREAS
        | set(CORRECTED_PREV_ID)
        | set(LevelCRC)
        - {LevelCRC.MAIN_MENU}
    )

    @classmethod
    def get(cls) -> int | LevelCRC:
        return cls.__update_previous_area_address()

    @classmethod
    def set(cls, value: Transition):
        """
        Sets the "previous area id" in memory.

        `value` is a `Transition` because this method tries to the fake ID
        to spawn the player on the proper entrance.

        If no mapping is found (ie: either value is incorrect),
        then `value.from_` is used directly,
        which at worst causes use the default entrance.
        """
        cls.__update_previous_area_address()
        memory.write_u32(
            cls._previous_area_address,
            cls.CORRECTED_TRANSITION_FROM.get(value, value.from_),
        )

    @classmethod
    def get_name(cls, area_id: int):
        """
        Gets the name of an area.

        If a "fake ID" is passed, it'll be mapped to the real "from level".
        """
        area = TRANSITION_INFOS_DICT.get(cls.CORRECTED_PREV_ID.get(area_id, area_id))
        return area.name if area else ""

    @classmethod
    def __update_previous_area_address(cls):
        # First check that the current value is a sensible known level
        previous_area = memory.read_u32(cls._previous_area_address)
        if previous_area in cls.__ALL_LEVELS:
            return previous_area

        # If not, start iterating over 16-bit blocks,
        # where the first half is consistent (a pointer?)
        # and the second half is maybe the value we're looking for
        block_address = memory.read_u32(ADDRESSES.previous_area_blocks_ptr)
        prefix = memory.read_u32(block_address)
        for _ in range(32):  # Limited iteration as extra safety for infinite loops
            # Check if the current block is a valid level id
            block_address += 8
            previous_area = memory.read_u32(block_address)
            if previous_area in cls.__ALL_LEVELS:
                # Valid id. Assume this is our address
                cls._previous_area_address = block_address
                return previous_area

            # Check if the next block is still part of the dynamic data
            block_address += 8
            next_prefix = memory.read_u32(block_address)
            if next_prefix != prefix:
                return -1  # We went the entire dynamic data structure w/o finding a valid ID !
        return -1


def dump_spoiler_logs(
    starting_area_name: str,
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    seed_string: SeedType,
):
    spoiler_logs = f"Starting area: {starting_area_name}\n"
    red_string_list = [
        f"{TRANSITION_INFOS_DICT[original[0]].name} "
        + f"({TRANSITION_INFOS_DICT[original[1]].name} exit) "
        + f"will redirect to: {TRANSITION_INFOS_DICT[redirect[1]].name} "
        + f"({TRANSITION_INFOS_DICT[redirect[0]].name} entrance)\n"
        for original, redirect in transitions_map.items()
    ]
    red_string_list.sort()
    for string in red_string_list:
        spoiler_logs += string

    unrandomized_transitions = ALL_POSSIBLE_TRANSITIONS - transitions_map.keys()
    if len(unrandomized_transitions) > 0:
        spoiler_logs += "\nUnrandomized transitions:\n"
        non_random_string_list = [
            f"From: {TRANSITION_INFOS_DICT[transition[0]].name}, "
            + f"To: {TRANSITION_INFOS_DICT[transition[1]].name}.\n"
            for transition in unrandomized_transitions
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
