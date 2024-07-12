from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from copy import copy
from enum import IntEnum
from pathlib import Path

from lib.constants import *  # noqa: F403
from lib.constants import __version__
from lib.entrance_rando import TRANSITION_INFOS_DICT_RANDO
from lib.types_ import SeedType


class Direction(IntEnum):
    ONEWAY = 1
    TWOWAY = 2


class LineType(IntEnum):
    SOLID = 1
    DASHED = 2


STARTING_AREA_COLOR = "#ff8000"  # Orange
UPGRADE_AREAS_COLOR = "#0080ff"  # Blue
IMPORTANT_STORY_TRIGGER_AREAS_COLOR = "#ff0000"  # Red
UPGRADE_AREAS = {
    LevelCRC.PLANE_COCKPIT,  # Canteen
    LevelCRC.BITTENBINDERS_CAMP,  # Sling + Rising Strike
    LevelCRC.MOUTH_OF_INTI,  # Torch
    LevelCRC.SCORPION_TEMPLE,  # Torch, temporary due to the current Scorpion Temple anti-softlock
    LevelCRC.NATIVE_VILLAGE,  # Shield
    LevelCRC.RENEGADE_HEADQUARTERS,  # Gas Mask
    LevelCRC.CAVERN_LAKE,  # Raft
    LevelCRC.MOUNTAIN_SLED_RUN,  # Raft
    LevelCRC.MOUNTAIN_OVERLOOK,  # Pickaxes
    LevelCRC.APU_ILLAPU_SHRINE,  # TNT
    LevelCRC.FLOODED_COURTYARD,  # Dash
    LevelCRC.TURTLE_MONUMENT,  # Dive
}
IMPORTANT_STORY_TRIGGER_AREAS = {
    LevelCRC.ALTAR_OF_AGES,
    LevelCRC.ST_CLAIRE_DAY,
    LevelCRC.GATES_OF_EL_DORADO,
}


def create_vertices(
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    starting_area: int,
):
    output_text = ""
    area_ids_randomized = set(
        chain(
            *(
                (original[0], redirect[1])
                for original, redirect
                in transitions_map.items()
            ),
        ),
    )
    counter_x = 0
    counter_y = 0
    for area_id in area_ids_randomized:
        # Currently St. Claire Night will never appear on the map,
        # so we remove the (Day) suffix as it's irrelevant and it clutters the map.
        # The same logic applies to the Spirit Fights:
        # these will never appear on the map, therefore we remove the (Harry) suffix.
        area_name = (
            TRANSITION_INFOS_DICT_RANDO
            [area_id]
            .name
            .replace(" (Day)", "")
            .replace(" (Harry)", "")
        )
        output_text += (
            f'<node positionX="{counter_x * 100 + counter_y * 20}" '
            + f'positionY="{counter_x * 50 + counter_y * 50}" '
            + f'id="{int(area_id)}" mainText="{area_name}"'
        )
        if area_id == starting_area:
            output_text += (
                ' ownStyles="{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;'
                + STARTING_AREA_COLOR
                + '&quot;}}"'
            )
        elif area_id in UPGRADE_AREAS:
            output_text += (
                ' ownStyles="{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;'
                + UPGRADE_AREAS_COLOR
                + '&quot;}}"'
            )
        elif area_id in IMPORTANT_STORY_TRIGGER_AREAS:
            output_text += (
                ' ownStyles="{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;'
                + IMPORTANT_STORY_TRIGGER_AREAS_COLOR
                + '&quot;}}"'
            )
        output_text += "></node>\n"
        row_length = 10
        counter_x += 1
        if counter_x == row_length:
            counter_x = 0
            counter_y += 1
    return output_text


def edge_text(
    start: int,
    end: int,
    counter: int,
    direct: Direction,
    color: str | None,
    line_type: LineType,
):
    direct_str = "true"
    if direct == Direction.TWOWAY:
        direct_str = "false"
    output = (
        f'<edge source="{TRANSITION_INFOS_DICT_RANDO[start].area_id}" '
        + f'target="{TRANSITION_INFOS_DICT_RANDO[end].area_id}" isDirect="{direct_str}" '
        + f'id="{counter}"'
    )
    if line_type == LineType.DASHED or color is not None:
        output += ' ownStyles="{&quot;0&quot;:{'
        if color is not None:
            output += f"&quot;strokeStyle&quot;:&quot;{color}&quot;"
            if line_type == LineType.DASHED:
                output += ","
        if line_type == LineType.DASHED:
            output += "&quot;lineDash&quot;:&quot;2&quot;"
        output += '}}"'
    output += "></edge>\n"
    return output


def create_edges(
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    temp_disabled_exits: list[tuple[int, int]],
    closed_door_exits: list[tuple[int, int]],
):
    connections = list(transitions_map.items())
    connections_two_way: list[tuple[tuple[int, int], tuple[int, int]]] = []
    connections_one_way: list[tuple[tuple[int, int], tuple[int, int]]] = []
    connections_closed_door: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for pairing in connections:
        reverse = (
            (pairing[1][1], pairing[1][0]),
            (pairing[0][1], pairing[0][0]),
        )
        if reverse not in connections_two_way and reverse not in connections_closed_door:
            if pairing[1] in closed_door_exits:
                connections_closed_door.append(pairing)
                continue
            if reverse[1] in closed_door_exits:
                continue
            if reverse in connections:
                connections_two_way.append(pairing)
            else:
                connections_one_way.append(pairing)

    output_text = ""
    counter = 1  # Can't start at 0 since that's the MAIN_MENU id
    for pairing in connections_two_way:
        if pairing[1] in temp_disabled_exits:
            output_text += edge_text(
                pairing[0][0], pairing[1][1],
                counter, Direction.TWOWAY, "#000000", LineType.SOLID,
            )
        else:
            output_text += edge_text(
                pairing[0][0], pairing[1][1],
                counter, Direction.TWOWAY, None, LineType.SOLID
            )
        counter += 1
    for pairing in connections_one_way:
        output_text += edge_text(
            pairing[0][0], pairing[1][1],
            counter, Direction.ONEWAY, None, LineType.DASHED
        )
        counter += 1
    for pairing in connections_closed_door:
        output_text += edge_text(
            pairing[1][1], pairing[0][0],
            counter, Direction.ONEWAY, "#ff0000", LineType.SOLID
        )
        counter += 1
    return output_text


def create_graphml(
    transitions_map: MutableMapping[tuple[int, int], tuple[int, int]],
    temp_disabled_exits: Sequence[tuple[int, int]],
    closed_door_exits: list[tuple[int, int]],
    seed_string: SeedType,
    starting_area: int,
):
    all_transitions = copy(transitions_map)
    for item in temp_disabled_exits:
        all_transitions[item] = item

    graphml_text = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        + '<graphml><graph id="Graph" uidGraph="1" uidEdge="1">\n'
        + create_vertices(all_transitions, starting_area)
        + create_edges(all_transitions, temp_disabled_exits, closed_door_exits)
        + "</graph></graphml>"
    )

    # TODO (Avasam): Get actual user folder based whether Dolphin Emulator is in AppData/Roaming
    # and if the current installation is portable.
    dolphin_path = Path().absolute()
    graphml_file = (
        dolphin_path
        / "User"
        / "Logs"
        / f"RANDOMIZED_MAP_v{__version__}_{seed_string}.graphml"
    )
    Path.write_text(graphml_file, graphml_text)
    print("Graphml file written to", graphml_file)
