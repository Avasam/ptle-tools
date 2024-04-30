from __future__ import annotations

import random
from collections.abc import Iterable

import CONFIGS
from lib.constants import *  # noqa: F403

_possible_starting_areas = [
    area for area in ALL_TRANSITION_AREAS
    # Remove impossible start areas + Don't immediately give TNT
    if area not in {APU_ILLAPU_SHRINE, SCORPION_TEMPLE, ST_CLAIRE_DAY}
    # Add back areas removed from transitions because of issues
] + [CRASH_SITE, TELEPORTERS]

starting_area = CONFIGS.STARTING_AREA or random.choice(_possible_starting_areas)


@dataclass
class State:
    # Initialize a few values to be used in loop
    current_area_old = 0
    """Area ID of the previous frame"""
    current_area_new = 0
    """Area ID of the current frame"""
    visited_altar_of_ages = False


state = State()


def get_prev_area_addr():
    """Used to set where you come from when you enter a new area."""
    addr = ADDRESSES.prev_area[0]
    for i in range(len(ADDRESSES.prev_area) - 1):
        addr = memory.read_u32(addr + ADDRESSES.prev_area[i + 1])
        if addr < GC_MIN_ADDRESS or addr > GC_MAX_ADDRESS:
            raise Exception(f"Invalid address {addr}")
    return addr


def highjack_transition_rando() -> int:  # pyright doesn't narrow `int | False` to just `int` after truthy check
    # Early return, faster check
    if state.current_area_old == state.current_area_new:
        return False

    redirect = transitions_map.get(state.current_area_old, {}).get(state.current_area_new)
    if not redirect:
        return False

    # Apply Altar of Ages logic to St. Claire's Excavation Camp
    if redirect in {ST_CLAIRE_DAY, ST_CLAIRE_NIGHT}:
        redirect = ST_CLAIRE_NIGHT if state.visited_altar_of_ages else ST_CLAIRE_DAY

    print(
        "highjack_transition_rando |",
        f"From: {hex(state.current_area_old)},",
        f"To: {hex(state.current_area_new)}.",
        f"Redirecting to: {hex(redirect)}",
    )
    memory.write_u32(ADDRESSES.current_area, redirect)
    return redirect


def highjack_transition(from_: int | None, to: int | None, redirect: int):
    if from_ is None:
        from_ = state.current_area_old
    if to is None:
        to = state.current_area_new
    if from_ == state.current_area_old and to == state.current_area_new:
        print(
            "highjack_transition |",
            f"From: {hex(state.current_area_old)},",
            f"To: {hex(state.current_area_new)}.",
            f"Redirecting to: {hex(redirect)}",
        )
        memory.write_u32(ADDRESSES.current_area, redirect)
        return True
    return False


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
"""```python
{
    from_id: {
        og_to_id: remapped_to_id
    }
}
```"""


def set_transitions_map():
    def _transition_map_set(from_: int, to: int, redirect: int):
        if transitions_map.get(from_):
            transitions_map[from_][to] = redirect
        else:
            transitions_map[from_] = {to: redirect}
    _possible_exits_bucket = ALL_POSSIBLE_EXITS.copy()
    """A temporary container of transitions to pick from until it is empty."""
    transitions_map.clear()
    for area in TRANSITION_INFOS_DICT.values():
        from_ = area.area_id
        for to_og in (exit_.area_id for exit_ in area.exits):
            redirect = get_random_redirection(from_, to_og, _possible_exits_bucket)
            if redirect is None or transitions_map.get(from_, {}).get(to_og):
                # Don't override something set in a previous iteration,
                # like from linked two-way entrances.
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
                    entrance = next(
                        exit_.area_id for exit_
                        in TRANSITION_INFOS_DICT[redirect].exits
                        if exit_.area_id in _possible_exits_bucket
                    )
                except IndexError:
                    # That area had more entrances than exits
                    continue
                _transition_map_set(redirect, entrance, from_)
                _possible_exits_bucket.remove(from_)
