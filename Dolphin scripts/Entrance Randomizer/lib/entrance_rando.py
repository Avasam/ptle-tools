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
    # Remove start areas that instantly softlock you + start areas that give too much progression
    if area not in {
        LevelCRC.APU_ILLAPU_SHRINE,
        LevelCRC.SCORPION_TEMPLE,
        LevelCRC.SCORPION_SPIRIT,
        LevelCRC.ST_CLAIRE_DAY,
        LevelCRC.ST_CLAIRE_NIGHT,
        LevelCRC.JAGUAR,
        LevelCRC.PUSCA
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

def check_part_of_loop(link, link_list, area_list):
    unchecked_links = []
    for l in link_list:
        unchecked_links.append(l)
    unchecked_links.remove(link)

    areas_reachable = [link[0]]
    new_area_reached = True
    while new_area_reached:
        new_area_reached = False
        new_links_reached = []
        for un in unchecked_links:
            if un[0] in areas_reachable or un[1] in areas_reachable:
                new_links_reached.append(un)
        if len(new_links_reached) > 0:
            new_area_reached = True
            for nl in new_links_reached:
                if not nl[0] in areas_reachable:
                    areas_reachable.append(nl[0])
                elif not nl[1] in areas_reachable:
                    areas_reachable.append(nl[1])
                unchecked_links.remove(nl)
    return len(areas_reachable) == len(area_list)

def link_two_levels(first, second):
    first.con_left -= 1
    second.con_left -= 1
    return [first, second]

def unlink_two_levels(first, second):
    first.con_left += 1
    second.con_left += 1


def set_transitions_map():
    transitions_map.clear()
    starting_default = TRANSITION_INFOS_DICT[starting_area].default_entrance
    tutorial_original = Transition(from_=LevelCRC.JAGUAR, to=LevelCRC.PLANE_CUTSCENE)
    tutorial_redirect = Transition(from_=starting_default, to=starting_area)
    transitions_map[tutorial_original] = tutorial_redirect

    _possible_redirections_bucket = list(starmap(Transition, ALL_POSSIBLE_TRANSITIONS))
    one_way_list = [
        Transition(from_=LevelCRC.WHITE_VALLEY, to=LevelCRC.MOUNTAIN_SLED_RUN),
        Transition(from_=LevelCRC.MOUNTAIN_SLED_RUN, to=LevelCRC.APU_ILLAPU_SHRINE),
        Transition(from_=LevelCRC.APU_ILLAPU_SHRINE, to=LevelCRC.WHITE_VALLEY),
        Transition(from_=LevelCRC.CAVERN_LAKE, to=LevelCRC.JUNGLE_CANYON)
    ]
    if CONFIGS.LINKED_TRANSITIONS:
        # Ground rules:
        # 1. you can't make a transition from a level to itself
        # 2. any 2 levels may have a maximum of 1 connection between them (as long as it's 2-way)

        _possible_origins_bucket = list(starmap(Transition, ALL_POSSIBLE_TRANSITIONS))

        level_list = []
        for area in TRANSITION_INFOS_DICT.values():
            area.con_left = len(area.exits)
            if area.con_left > 0:
                level_list.append(area)
        random.shuffle(level_list)
        level_list.sort(key=lambda a: a.con_left, reverse=True)

        link_list = []
        link_list.append(link_two_levels(level_list[0], level_list[1]))

        total_con_left = level_list[0].con_left + level_list[1].con_left

        index = 2
        while index < len(level_list):
            r = random.choice([1, 2])
            if total_con_left > 0 and (level_list[index].con_left < 2 or r == 1):
                # option 1: connect to one or more existing levels
                total_con_left += level_list[index].con_left
                levels_available = []
                for i in range(len(level_list)):
                    if i == index:
                        break
                    if level_list[i].con_left > 0:
                        levels_available.append(level_list[i])
                amount_chosen = random.randint(1, min(level_list[index].con_left, len(levels_available)))
                levels_chosen = random.sample(levels_available, amount_chosen)
                for level_chosen in levels_chosen:
                    link_list.append(link_two_levels(level_list[index], level_chosen))
                    total_con_left -= 2
            elif level_list[index].con_left >= 2 and (total_con_left == 0 or r == 2):
                # option 2: put the current level inbetween an already established connection
                total_con_left += level_list[index].con_left
                level_a, level_b = link_list.pop(random.randrange(len(link_list)))
                unlink_two_levels(level_a, level_b)
                link_list.append(link_two_levels(level_list[index], level_a))
                link_list.append(link_two_levels(level_list[index], level_b))
                total_con_left -= 2
            else:
                # option 3: break open a connection that's part of a level loop, then restart this iteration
                direc = random.choice([-1, 1])
                link_i = random.randrange(len(link_list))
                valid_link = False
                while not valid_link:
                    linked_areas = []
                    for i in range(len(level_list)):
                        if i == index:
                            break
                        linked_areas.append(level_list[i])
                    valid_link = check_part_of_loop(link_list[link_i], link_list, linked_areas)
                    if not valid_link:
                        link_i += direc
                        if link_i == len(link_list):
                            link_i = 0
                        elif link_i < 0:
                            link_i += len(link_list)
                level_a, level_b = link_list.pop(link_i)
                unlink_two_levels(level_a, level_b)
                total_con_left += 2
                continue
            index += 1

        for link in link_list:
            options_original = [
                trans for trans in _possible_origins_bucket
                if trans.from_ == link[0].area_id
            ]
            options_redirect = [
                trans for trans in _possible_redirections_bucket
                if trans.to == link[1].area_id
            ]
            original = random.choice(options_original)
            redirect = random.choice(options_redirect)
            transitions_map[original] = redirect
            _possible_origins_bucket.remove(original)
            _possible_redirections_bucket.remove(redirect)

            counterpart_original = Transition(from_=redirect.to, to=redirect.from_)
            counterpart_redirect = Transition(from_=original.to, to=original.from_)
            transitions_map[counterpart_original] = counterpart_redirect
            _possible_origins_bucket.remove(counterpart_original)
            _possible_redirections_bucket.remove(counterpart_redirect)

        one_way_redirects = one_way_list.copy()
        random.shuffle(one_way_redirects)
        for original in one_way_list:
            if one_way_redirects[0].to == original.from_:
                transitions_map[original] = one_way_redirects.pop(1)
            else:
                 transitions_map[original] = one_way_redirects.pop(0)
    else:
        # Ground rules:
        # 1. you can't make a transition from a level to itself
        for trans in one_way_list:
            _possible_redirections_bucket.append(trans)

        for area in TRANSITION_INFOS_DICT.values():
            for to_og in (exit_.area_id for exit_ in area.exits):
                original = Transition(from_=area.area_id, to=to_og)
                redirect = get_random_redirection(original, _possible_redirections_bucket)
                transitions_map[original] = redirect
                _possible_redirections_bucket.remove(redirect)
        for original in one_way_list:
            redirect = get_random_redirection(original, _possible_redirections_bucket)
            transitions_map[original] = redirect
            _possible_redirections_bucket.remove(redirect)

