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


def create_graphml(
    transitions_map: Mapping[tuple[int, int], tuple[int, int]],
    seed_string: SeedType,
    starting_area: int
):
    graphml_text = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><graphml><graph id=\"Graph\" uidGraph=\"1\" uidEdge=\"1\">\n"
    counter_x = 0
    counter_y = 0
    for area in TRANSITION_INFOS_DICT.values():
        graphml_text += (
            f"<node positionX=\"{counter_x * 100 + counter_y * 20}\" positionY=\"{counter_x * 50 + counter_y * 50}\" "
            + f"id=\"{area.small_id}\" mainText=\"{area.name}\" "
        )
        # Starting area: Orange
        if area.area_id == starting_area:
            graphml_text += "ownStyles = \"{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;#ff8000&quot;}}\" "
        # Area with Upgrade: Blue
        elif area.area_id in (
            LevelCRC.FLOODED_COURTYARD,
            LevelCRC.TURTLE_MONUMENT,
            LevelCRC.PLANE_COCKPIT,
            LevelCRC.BITTENBINDERS_CAMP,
            LevelCRC.MOUTH_OF_INTI,
            LevelCRC.NATIVE_VILLAGE,
            LevelCRC.RENEGADE_HEADQUARTERS,
            LevelCRC.CAVERN_LAKE,
            LevelCRC.MOUNTAIN_SLED_RUN,
            LevelCRC.MOUNTAIN_OVERLOOK,
            LevelCRC.APU_ILLAPU_SHRINE
        ):
            graphml_text += "ownStyles = \"{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;#0080ff&quot;}}\" "
        # Important Story Triggers: Red
        elif area.area_id in (
            LevelCRC.ALTAR_OF_AGES,
            LevelCRC.ST_CLAIRE_DAY,
            LevelCRC.ST_CLAIRE_NIGHT,
            LevelCRC.GATES_OF_EL_DORADO
        ):
            graphml_text += "ownStyles = \"{&quot;0&quot;:{&quot;fillStyle&quot;:&quot;#ff0000&quot;}}\" "
        graphml_text += "></node>\n"
        if counter_x == 9:
            counter_x = 0
            counter_y += 1
        else:
            counter_x += 1
    connections = []
    connections_two_way = []
    connections_one_way = []
    for original, redirect in transitions_map.items():
        connections.append([original[0], redirect[1]])
    for pairing in connections:
        if not [pairing[1], pairing[0]] in connections_two_way:
            if [pairing[1], pairing[0]] in connections:
                connections_two_way.append(pairing)
            else:
                connections_one_way.append(pairing)
    counter = 10000
    for pairing in connections_two_way:
        graphml_text += (
            f"<edge source=\"{TRANSITION_INFOS_DICT[pairing[0]].small_id}\" "
            + f"target=\"{TRANSITION_INFOS_DICT[pairing[1]].small_id}\" isDirect=\"false\" "
            + f"weight=\"1\" useWeight=\"false\" id=\"{counter}\" text=\"\" upText=\"\" "
            + f"arrayStyleStart=\"\" arrayStyleFinish=\"\" model_width=\"4\" model_type=\"0\" "
            + f"model_curveValue=\"0.1\" model_default=\"NaN\" ></edge>\n"
        )
        counter += 1
    for pairing in connections_one_way:
        graphml_text += (
            f"<edge source=\"{TRANSITION_INFOS_DICT[pairing[0]].small_id}\" "
            + f"target=\"{TRANSITION_INFOS_DICT[pairing[1]].small_id}\" isDirect=\"true\" "
            + f"weight=\"1\" useWeight=\"false\" id=\"{counter}\" text=\"\" upText=\"\" "
            + f"arrayStyleStart=\"\" arrayStyleFinish=\"\" model_width=\"4\" model_type=\"0\" "
            + f"model_curveValue=\"0.1\" model_default=\"true\" ></edge>\n"
        )
        counter += 1
    graphml_text += "</graph></graphml>"

    # TODO (Avasam): Get actual user folder based whether Dolphin Emulator is in AppData/Roaming
    # and if the current installation is portable.
    dolphin_path = Path().absolute()
    graphml_file = (
        dolphin_path
        / "User"
        / "Logs"
        / f"MY_GRAPH_v{__version__}_{seed_string}.graphml"
    )
    Path.write_text(graphml_file, graphml_text)
    print("Graphml file written to", graphml_file)

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

    unrandomized_transitions = ALL_POSSIBLE_TRANSITIONS - transitions_map.keys()
    if len(unrandomized_transitions) > 0:
        spoiler_logs += "\nUnrandomized transitions:\n"
        for transition in unrandomized_transitions:
            spoiler_logs += (
                f"From: {TRANSITION_INFOS_DICT[transition[0]].name}, "
                + f"To: {TRANSITION_INFOS_DICT[transition[1]].name}.\n"
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
