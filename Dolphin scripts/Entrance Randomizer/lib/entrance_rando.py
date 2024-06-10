from __future__ import annotations

import random
from collections.abc import Iterable
from itertools import starmap
from typing import NamedTuple

import CONFIGS
from lib.constants import *  # noqa: F403
from lib.utils import follow_pointer_path, state

_possible_starting_areas = [
    area for area in ALL_TRANSITION_AREAS
    # Remove impossible start areas + Don't immediately give TNT
    if area not in {
        LevelCRC.APU_ILLAPU_SHRINE,
        LevelCRC.SCORPION_TEMPLE,
        LevelCRC.ST_CLAIRE_DAY,
    }
]

starting_area = CONFIGS.STARTING_AREA or random.choice(_possible_starting_areas)


class Transition(NamedTuple):
    from_: int
    to: int


def highjack_transition_rando():
    # Early return, faster check. Detect the start of a transition
    if state.current_area_old == state.current_area_new:
        return False

    redirect = transitions_map.get((state.current_area_old, state.current_area_new))
    if not redirect:
        return False

    # Apply Altar of Ages logic to St. Claire's Excavation Camp
    if redirect.to in {LevelCRC.ST_CLAIRE_DAY, LevelCRC.ST_CLAIRE_NIGHT}:
        redirect = Transition(
            redirect.from_,
            to=LevelCRC.ST_CLAIRE_NIGHT if state.visited_altar_of_ages else LevelCRC.ST_CLAIRE_DAY,
        )

    print(
        "highjack_transition_rando |",
        f"From: {hex(state.current_area_old)},",
        f"To: {hex(state.current_area_new)}.",
        f"Redirecting to: {hex(redirect.to)}",
        f"({hex(redirect.from_)} entrance)\n",
    )
    memory.write_u32(follow_pointer_path(ADDRESSES.prev_area), redirect.from_)
    memory.write_u32(ADDRESSES.current_area, redirect.to)
    state.current_area_new = redirect[1]
    return redirect


def highjack_transition(from_: int | None, to: int | None, redirect: int):
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


def get_random_redirection(original: Transition, possible_redirections: Iterable[Transition]):
    possible_redirections = [
        redirect for redirect in possible_redirections
        # Prevent looping on itself
        if original.from_ != redirect.to
    ]
    # Investigate and explain why that can happen
    return random.choice(possible_redirections) \
        if len(possible_redirections) > 0 \
        else None


transitions_map: dict[tuple[int, int], Transition] = {}
"""```python
{
    (og_from_id, og_to_id): (og_from_id, og_to_id)
}
```"""


def set_transitions_map():
    _possible_transitions_bucket = list(starmap(Transition, ALL_POSSIBLE_TRANSITIONS))
    """A temporary container of transitions to pick from until it is empty."""
    transitions_map.clear()
    if not CONFIGS.SKIP_JAGUAR:
        starting_default = TRANSITION_INFOS_DICT[starting_area].default_entrance
        tutorial_original = Transition(from_=LevelCRC.JAGUAR, to=LevelCRC.PLANE_CUTSCENE)
        tutorial_redirect = Transition(from_=starting_default, to=starting_area)
        transitions_map[tutorial_original] = tutorial_redirect

    for area in TRANSITION_INFOS_DICT.values():
        for to_og in (exit_.area_id for exit_ in area.exits):
            original = Transition(from_=area.area_id, to=to_og)
            redirect = get_random_redirection(original, _possible_transitions_bucket)
            if redirect is None or original in transitions_map:
                # Don't override something set in a previous iteration,
                # like from linked two-way entrances.
                continue

            transitions_map[original] = redirect
            _possible_transitions_bucket.remove(redirect)

            if CONFIGS.LINKED_TRANSITIONS:
                # Ensure we haven't already expanded all transitions back to the "from" area.
                # (I think that means that area had more exits than entrances)
                # if original.from_ not in (
                #         transition.to for transition in _possible_transitions_bucket
                # ):
                #     continue
                flipped_redirect = Transition(from_=redirect.to, to=redirect.from_)
                flipped_original = Transition(from_=original.to, to=original.from_)
                # Ensure that the transition is even possible to reverse
                # (neither entrance nor exists should be one-way)
                if (
                    flipped_redirect not in ALL_POSSIBLE_TRANSITIONS
                    or flipped_original not in _possible_transitions_bucket
                ):
                    continue
                transitions_map[flipped_redirect] = flipped_original
                _possible_transitions_bucket.remove(flipped_original)
