from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from lib.constants import *  # noqa: F403
from lib.constants import __version__
from lib.transition_infos import Area
from lib.types_ import SeedType


def create_vertices(
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    starting_area: int,
):
    output_text = ""
    areas_randomized: list[Area] = []
    for original, redirect in transitions_map.items():
        if TRANSITION_INFOS_DICT[original[0]] not in areas_randomized:
            areas_randomized.append(TRANSITION_INFOS_DICT[original[0]])
        if TRANSITION_INFOS_DICT[redirect[1]] not in areas_randomized:
            areas_randomized.append(TRANSITION_INFOS_DICT[redirect[1]])
    counter_x = 0
    counter_y = 0
    for area in areas_randomized:
        output_text += (
            f'<node positionX="{counter_x * 100 + counter_y * 20}" '
            + f'positionY="{counter_x * 50 + counter_y * 50}" '
            + f'id="{area.small_id}" mainText="{area.name}" '
        )
        # Starting area: Orange
        if area.area_id == starting_area:
            output_text += (
                'ownStyles = "{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;#ff8000&quot;}}" '
            )
        # Areas with Upgrades: Blue
        elif area.area_id in {
            LevelCRC.PLANE_COCKPIT,
            LevelCRC.BITTENBINDERS_CAMP,
            LevelCRC.MOUTH_OF_INTI,
            LevelCRC.FLOODED_COURTYARD,
            LevelCRC.TURTLE_MONUMENT,
            LevelCRC.NATIVE_VILLAGE,
            LevelCRC.RENEGADE_HEADQUARTERS,
            LevelCRC.CAVERN_LAKE,
            LevelCRC.MOUNTAIN_SLED_RUN,
            LevelCRC.MOUNTAIN_OVERLOOK,
            LevelCRC.APU_ILLAPU_SHRINE,
        }:
            output_text += (
                'ownStyles = "{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;#0080ff&quot;}}" '
            )
        # Important Story Triggers: Red
        elif area.area_id in {
            LevelCRC.ALTAR_OF_AGES,
            LevelCRC.ST_CLAIRE_DAY,
            LevelCRC.ST_CLAIRE_NIGHT,
            LevelCRC.GATES_OF_EL_DORADO,
        }:
            output_text += (
                'ownStyles = "{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;#ff0000&quot;}}" '
            )
        output_text += "></node>\n"
        row_length = 10
        counter_x += 1
        if counter_x == row_length:
            counter_x = 0
            counter_y += 1
    return output_text


def create_edges(transitions_map: Mapping[tuple[int, int], tuple[int, int]]):
    output_text = ""
    connections: list[tuple[tuple[int, int], tuple[int, int]]] = []
    connections_two_way: list[tuple[tuple[int, int], tuple[int, int]]] = []
    connections_one_way: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for original, redirect in transitions_map.items():
        connections.append([original[0], redirect[1]])
    for pairing in connections:
        if [pairing[1], pairing[0]] not in connections_two_way:
            if [pairing[1], pairing[0]] in connections:
                connections_two_way.append(pairing)
            else:
                connections_one_way.append(pairing)
    counter = 10000
    for pairing in connections_two_way:
        output_text += (
            f'<edge source="{TRANSITION_INFOS_DICT[pairing[0]].small_id}" '
            + f'target="{TRANSITION_INFOS_DICT[pairing[1]].small_id}" isDirect="false" '
            + f'id="{counter}" ></edge>\n'
        )
        counter += 1
    for pairing in connections_one_way:
        output_text += (
            f'<edge source="{TRANSITION_INFOS_DICT[pairing[0]].small_id}" '
            + f'target="{TRANSITION_INFOS_DICT[pairing[1]].small_id}" isDirect="true" '
            + f'id="{counter}" ></edge>\n'
        )
        counter += 1
    return output_text


def create_graphml(
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    seed_string: SeedType,
    starting_area: int,
):

    graphml_text = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        + '<graphml><graph id="Graph" uidGraph="1" uidEdge="1">\n'
        + create_vertices(transitions_map, starting_area)
        + create_edges(transitions_map)
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
