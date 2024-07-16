from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from enum import IntEnum, auto
from pathlib import Path

from lib.constants import *  # noqa: F403
from lib.constants import __version__
from lib.types_ import SeedType


class Direction(IntEnum):
    ONEWAY = auto()
    TWOWAY = auto()


class LineType(IntEnum):
    SOLID = auto()
    DASHED = auto()


STARTING_AREA_COLOR = "#ff8000"  # Orange
UPGRADE_AREAS_COLOR = "#0080ff"  # Blue
IMPORTANT_STORY_TRIGGER_AREAS_COLOR = "#ff0000"  # Red
UNRANDOMIZED_EDGE_COLOR = "#000000"  # Black

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


def create_own_style(params: dict[str, str | None]):
    style = ", ".join([
        f"&quot;{key}&quot;:&quot;{value}&quot;"
        for key, value in params.items()
        if value is not None
    ])
    return ' ownStyles="{&quot;0&quot;:{' + style + '}}"' if style else ""


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
            TRANSITION_INFOS_DICT
            [area_id]
            .name
            .replace(" (Day)", "")
            .replace(" (Harry)", "")
        )
        output_text += (
            f'<node positionX="{counter_x * 100 + counter_y * 20}" '
            + f'positionY="{counter_x * 50 + counter_y * 50}" '
            + f'id="{int(area_id)}" '
            + f'mainText="{area_name}"'
        )
        if area_id == starting_area:
            output_text += create_own_style({"fillStyle": STARTING_AREA_COLOR})
        elif area_id in UPGRADE_AREAS:
            output_text += create_own_style({"fillStyle": UPGRADE_AREAS_COLOR})
        elif area_id in IMPORTANT_STORY_TRIGGER_AREAS:
            output_text += create_own_style({"fillStyle": IMPORTANT_STORY_TRIGGER_AREAS_COLOR})
        output_text += "></node>\n"
        row_length = 10
        counter_x += 1
        if counter_x == row_length:
            counter_x = 0
            counter_y += 1
    return output_text


def edge_component(
    start: int,
    end: int,
    counter: int,
    direct: Direction,
    color: str | None,
    line_type: LineType,
):
    direct_str = str(direct == Direction.ONEWAY).lower()
    return (
        f'<edge source="{TRANSITION_INFOS_DICT[start].area_id}" '
        + f'target="{TRANSITION_INFOS_DICT[end].area_id}" '
        + f'isDirect="{direct_str}" '
        + f'id="{counter}"'
        + create_own_style({
            "strokeStyle": color,
            "lineDash": "2" if line_type == LineType.DASHED else None,
        })
        + "></edge>\n"
    )


def create_edges(
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    shown_disabled_transitions: Iterable[tuple[int, int]],
):
    connections = list(transitions_map.items())
    connections_two_way: list[tuple[tuple[int, int], tuple[int, int]]] = []
    connections_one_way: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for pairing in connections:
        reverse = (
            (pairing[1][1], pairing[1][0]),
            (pairing[0][1], pairing[0][0]),
        )
        if reverse not in connections_two_way:
            if reverse in connections:
                connections_two_way.append(pairing)
            else:
                connections_one_way.append(pairing)

    output_text = ""
    counter = 1  # Can't start at 0 since that's the MAIN_MENU id
    for pairing in connections_two_way:
        output_text += edge_component(
            pairing[0][0],
            pairing[1][1],
            counter,
            Direction.TWOWAY,
            UNRANDOMIZED_EDGE_COLOR if pairing[1] in shown_disabled_transitions else None,
            LineType.SOLID,
        )
        counter += 1
    for pairing in connections_one_way:
        output_text += edge_component(
            pairing[0][0],
            pairing[1][1],
            counter,
            Direction.ONEWAY,
            None,
            LineType.DASHED,
        )
        counter += 1
    return output_text


def create_graphml(
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    shown_disabled_transitions: Sequence[tuple[int, int]],
    seed_string: SeedType,
    starting_area: int,
):
    all_transitions = dict(transitions_map) | {item: item for item in shown_disabled_transitions}

    graphml_text = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        + '<graphml><graph id="Graph" uidGraph="1" uidEdge="1">\n'
        + create_vertices(all_transitions, starting_area)
        + create_edges(all_transitions, shown_disabled_transitions)
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
