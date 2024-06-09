from __future__ import annotations

import random
from collections.abc import Iterable, MutableMapping, Sequence
from enum import IntEnum
from itertools import starmap
from typing import NamedTuple, Sized

import CONFIGS
from lib.constants import *  # noqa: F403
from lib.transition_infos import Area
from lib.utils import follow_pointer_path, state


class Transition(NamedTuple):
    from_: int
    to: int


class Choice(IntEnum):
    CONNECT = 1
    INBETWEEN = 2


_possible_starting_areas = [
    area for area in ALL_TRANSITION_AREAS
    # Remove certain starting areas from the list of possibilities
    if area not in {
        # These areas will instantly softlock you
        LevelCRC.APU_ILLAPU_SHRINE,
        LevelCRC.SCORPION_TEMPLE,
        LevelCRC.SCORPION_SPIRIT,
        # These areas will give too much progression
        LevelCRC.ST_CLAIRE_DAY,  # gives TNT
        LevelCRC.ST_CLAIRE_NIGHT,  # gives all items + access to El Dorado
        LevelCRC.JAGUAR,  # sends to final bosses
        LevelCRC.PUSCA,  # sends to final bosses
        # Temples and spirits are effectively duplicates, so we remove half of them here
        LevelCRC.MONKEY_TEMPLE,
        LevelCRC.PENGUIN_TEMPLE,
    }
]

# Call RNG even if this is unused to not impact randomization of other things for the same seed
starting_area = random.choice(_possible_starting_areas)
if CONFIGS.STARTING_AREA is not None:
    starting_area = CONFIGS.STARTING_AREA

transitions_map: dict[tuple[int, int], Transition] = {}
"""```python
{
    (og_from_id, og_to_id): (og_from_id, og_to_id)
}
```"""

disabled_exits: list[tuple[int, int]] = [
    # Temporarily disabled levels
    (LevelCRC.EYES_OF_DOOM, LevelCRC.SCORPION_TEMPLE),
    (LevelCRC.SCORPION_TEMPLE, LevelCRC.EYES_OF_DOOM),
    (LevelCRC.ALTAR_OF_HUITACA, LevelCRC.MOUTH_OF_INTI),
    (LevelCRC.MOUTH_OF_INTI, LevelCRC.ALTAR_OF_HUITACA),
    (LevelCRC.TWIN_OUTPOSTS, LevelCRC.TWIN_OUTPOSTS_UNDERWATER),
    (LevelCRC.TWIN_OUTPOSTS_UNDERWATER, LevelCRC.TWIN_OUTPOSTS),
    # The 4 one-way exits
    (LevelCRC.WHITE_VALLEY, LevelCRC.MOUNTAIN_SLED_RUN),
    (LevelCRC.MOUNTAIN_SLED_RUN, LevelCRC.APU_ILLAPU_SHRINE),
    (LevelCRC.APU_ILLAPU_SHRINE, LevelCRC.WHITE_VALLEY),
    (LevelCRC.CAVERN_LAKE, LevelCRC.JUNGLE_CANYON),
    # The 3 Spirit Fights
    (LevelCRC.MONKEY_TEMPLE, LevelCRC.MONKEY_SPIRIT),
    (LevelCRC.MONKEY_SPIRIT, LevelCRC.MONKEY_TEMPLE),
    (LevelCRC.SCORPION_TEMPLE, LevelCRC.SCORPION_SPIRIT),
    (LevelCRC.SCORPION_SPIRIT, LevelCRC.SCORPION_TEMPLE),
    (LevelCRC.PENGUIN_TEMPLE, LevelCRC.PENGUIN_SPIRIT),
    (LevelCRC.PENGUIN_SPIRIT, LevelCRC.PENGUIN_TEMPLE),
    # The 5 Native Games
    (LevelCRC.NATIVE_VILLAGE, LevelCRC.WHACK_A_TUCO),
    (LevelCRC.WHACK_A_TUCO, LevelCRC.NATIVE_VILLAGE),
    (LevelCRC.NATIVE_VILLAGE, LevelCRC.TUCO_SHOOT),
    (LevelCRC.TUCO_SHOOT, LevelCRC.NATIVE_VILLAGE),
    (LevelCRC.NATIVE_VILLAGE, LevelCRC.RAFT_BOWLING),
    (LevelCRC.RAFT_BOWLING, LevelCRC.NATIVE_VILLAGE),
    (LevelCRC.NATIVE_VILLAGE, LevelCRC.PICKAXE_RACE),
    (LevelCRC.PICKAXE_RACE, LevelCRC.NATIVE_VILLAGE),
    (LevelCRC.NATIVE_VILLAGE, LevelCRC.KABOOM),
    (LevelCRC.KABOOM, LevelCRC.NATIVE_VILLAGE),
    # The 2 CUTSCENE Levels
    (LevelCRC.JAGUAR, LevelCRC.PLANE_CUTSCENE),
    (LevelCRC.PLANE_CUTSCENE, LevelCRC.CRASH_SITE),
    (LevelCRC.SPINJA_LAIR, LevelCRC.VIRACOCHA_MONOLITHS_CUTSCENE),
    (LevelCRC.VIRACOCHA_MONOLITHS_CUTSCENE, LevelCRC.VIRACOCHA_MONOLITHS),
    # Specific one-time, one-way warps
    (LevelCRC.ALTAR_OF_AGES, LevelCRC.BITTENBINDERS_CAMP),
    (LevelCRC.ST_CLAIRE_DAY, LevelCRC.ST_CLAIRE_NIGHT),
    (LevelCRC.ST_CLAIRE_NIGHT, LevelCRC.ST_CLAIRE_DAY),
    (LevelCRC.GATES_OF_EL_DORADO, LevelCRC.JAGUAR),
    (LevelCRC.JAGUAR, LevelCRC.PUSCA),
    (LevelCRC.PUSCA, LevelCRC.GATES_OF_EL_DORADO),
    # The Unused Beta Volcano Level
    (LevelCRC.BETA_VOLCANO, LevelCRC.JUNGLE_CANYON),
    (LevelCRC.BETA_VOLCANO, LevelCRC.PLANE_COCKPIT),
]


def remove_disabled_exits():
    global ALL_POSSIBLE_TRANSITIONS
    ALL_POSSIBLE_TRANSITIONS = tuple(  # pyright: ignore[reportConstantRedefinition]
        filter(lambda x: x not in disabled_exits, ALL_POSSIBLE_TRANSITIONS),
    )
    for disabled in disabled_exits:
        for area in TRANSITION_INFOS_DICT.values():
            if area.area_id == disabled[0]:
                for ex in area.exits:
                    if ex.area_id == disabled[1]:
                        area.exits = tuple(filter(lambda x: x != ex, area.exits))
                        break
                break


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
        return True
    return False


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


def link_two_levels(first: Area, second: Area):
    first.con_left -= 1
    second.con_left -= 1
    return (first, second)


def unlink_two_levels(first: Area, second: Area):
    first.con_left += 1
    second.con_left += 1


def connect_to_existing(
    level_list: Sequence[Area],
    index: int,
    link_list: list[tuple[Area, Area]],
):
    global total_con_left
    total_con_left += level_list[index].con_left
    levels_available: list[Area] = []
    for i in range(len(level_list)):
        if i == index:
            break
        if level_list[i].con_left > 0:
            levels_available.append(level_list[i])
    amount_chosen = random.randint(
        1, min(level_list[index].con_left, len(levels_available)),
    )
    levels_chosen = random.sample(levels_available, amount_chosen)
    for level_chosen in levels_chosen:
        link_list.append(link_two_levels(level_list[index], level_chosen))
        total_con_left -= 2


def check_part_of_loop(
    link: tuple[Area, Area],
    link_list: list[tuple[Area, Area]],
    area_list: Sized,
):
    unchecked_links = link_list.copy()
    unchecked_links.remove(link)
    areas_reachable = [link[0]]
    new_area_reached = True
    while new_area_reached:
        new_area_reached = False
        new_links_reached = [
            x for x in unchecked_links if (x[0] in areas_reachable or x[1] in areas_reachable)
        ]
        if len(new_links_reached) > 0:
            new_area_reached = True
            for nl in new_links_reached:
                if nl[0] not in areas_reachable:
                    areas_reachable.append(nl[0])
                elif nl[1] not in areas_reachable:
                    areas_reachable.append(nl[1])
                unchecked_links.remove(nl)
    return len(areas_reachable) == len(area_list)


def break_open_connection(
    level_list: Sequence[Area],
    index: int,
    link_list: list[tuple[Area, Area]],
):
    global total_con_left
    direc = random.choice([-1, 1])
    link_i = random.randrange(len(link_list))
    valid_link = False
    while not valid_link:
        linked_areas: list[Area] = []
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


def link_list_to_transitions(
    link_list: list[tuple[Area, Area]],
    transitions_map: MutableMapping[tuple[int, int], Transition],
    origins_bucket: list[Transition],
    redirections_bucket: list[Transition],
):
    for link in link_list:
        options_original = [
            trans for trans in origins_bucket
            if trans.from_ == link[0].area_id
        ]
        options_redirect = [
            trans for trans in redirections_bucket
            if trans.to == link[1].area_id
        ]
        original = random.choice(options_original)
        redirect = random.choice(options_redirect)
        transitions_map[original] = redirect
        origins_bucket.remove(original)
        redirections_bucket.remove(redirect)

        counterpart_original = Transition(from_=redirect.to, to=redirect.from_)
        counterpart_redirect = Transition(from_=original.to, to=original.from_)
        transitions_map[counterpart_original] = counterpart_redirect
        origins_bucket.remove(counterpart_original)
        redirections_bucket.remove(counterpart_redirect)


def get_random_redirection(original: Transition, all_redirections: Iterable[Transition]):
    possible_redirections = [
        redirect for redirect in all_redirections
        if original.from_ != redirect.to  # Prevent looping on itself
    ]
    if len(possible_redirections) > 0:
        return random.choice(possible_redirections)
    return None


def set_transitions_map():
    transitions_map.clear()
    if not CONFIGS.SKIP_JAGUAR:
        starting_default = TRANSITION_INFOS_DICT[starting_area].default_entrance
        tutorial_original = Transition(from_=LevelCRC.JAGUAR, to=LevelCRC.PLANE_CUTSCENE)
        tutorial_redirect = Transition(from_=starting_default, to=starting_area)
        transitions_map[tutorial_original] = tutorial_redirect

    _possible_redirections_bucket = list(starmap(Transition, ALL_POSSIBLE_TRANSITIONS))
    one_way_list = [
        Transition(from_=LevelCRC.WHITE_VALLEY, to=LevelCRC.MOUNTAIN_SLED_RUN),
        Transition(from_=LevelCRC.MOUNTAIN_SLED_RUN, to=LevelCRC.APU_ILLAPU_SHRINE),
        Transition(from_=LevelCRC.APU_ILLAPU_SHRINE, to=LevelCRC.WHITE_VALLEY),
        Transition(from_=LevelCRC.CAVERN_LAKE, to=LevelCRC.JUNGLE_CANYON),
    ]
    if CONFIGS.LINKED_TRANSITIONS:
        # Ground rules:
        # 1. you can't make a transition from a level to itself
        # 2. any 2 levels may have a maximum of 1 connection between them (as long as it's 2-way)

        _possible_origins_bucket = list(starmap(Transition, ALL_POSSIBLE_TRANSITIONS))

        level_list: list[Area] = []
        for area in TRANSITION_INFOS_DICT.values():
            area.con_left = len(area.exits)
            if area.con_left > 0:
                level_list.append(area)
        random.shuffle(level_list)
        level_list.sort(key=lambda a: a.con_left, reverse=True)

        link_list = [link_two_levels(level_list[0], level_list[1])]
        global total_con_left
        total_con_left = level_list[0].con_left + level_list[1].con_left

        index = 2
        while index < len(level_list):
            choice = random.choice([Choice.CONNECT, Choice.INBETWEEN])
            if total_con_left > 0 and (
                level_list[index].con_left == 1 or choice == Choice.CONNECT
            ):
                # option 1: connect to one or more existing levels
                connect_to_existing(level_list, index, link_list)
            elif level_list[index].con_left > 1 and (
                total_con_left == 0 or choice == Choice.INBETWEEN
            ):
                # option 2: put the current level inbetween an already established connection
                total_con_left += level_list[index].con_left
                level_a, level_b = link_list.pop(random.randrange(len(link_list)))
                unlink_two_levels(level_a, level_b)
                link_list.extend((
                    link_two_levels(level_list[index], level_a),
                    link_two_levels(level_list[index], level_b),
                ))
                total_con_left -= 2
            else:
                # option 3: break open a connection that's part of a level loop,
                # then restart this iteration
                break_open_connection(level_list, index, link_list)
                continue
            index += 1

        link_list_to_transitions(
            link_list,
            transitions_map,
            _possible_origins_bucket,
            _possible_redirections_bucket,
        )

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
        _possible_redirections_bucket.extend(one_way_list)
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
