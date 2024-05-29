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
        return True
    return False


def get_random_redirection(original: Transition, all_redirections: Iterable[Transition]):
    possible_redirections = [
        redirect for redirect in all_redirections
        if original.from_ != redirect.to # Prevent looping on itself
    ]
    if len(possible_redirections) > 0:
        return random.choice(possible_redirections)
    else:
        return None


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
    for area in TRANSITION_INFOS_DICT.values():
        for to_og in (exit_.area_id for exit_ in area.exits):
            original = Transition(from_=area.area_id, to=to_og)
            if original in transitions_map:
                continue # if we already did this one: skip it

            redirect = get_random_redirection(original, _possible_transitions_bucket)
            if redirect is None:
                continue # if no redirect is found: skip it

            transitions_map[original] = redirect
            _possible_transitions_bucket.remove(redirect)

            if CONFIGS.LINKED_TRANSITIONS:
                counterpart_original = Transition(from_=redirect.to, to=redirect.from_)
                counterpart_redirect = Transition(from_=original.to, to=original.from_)

                if (counterpart_redirect not in ALL_POSSIBLE_TRANSITIONS):
                    continue # if a transition in this direction doesn't exist (the original was a one-way): skip it
                if (counterpart_redirect not in _possible_transitions_bucket):
                    continue # if the reverse transition was already used up: skip it

                transitions_map[counterpart_original] = counterpart_redirect
                _possible_transitions_bucket.remove(counterpart_redirect)
