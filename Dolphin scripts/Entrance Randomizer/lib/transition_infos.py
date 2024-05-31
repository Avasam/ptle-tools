from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, TypedDict


class ExitJSON(TypedDict):
    area_id: str
    area_name: str
    requires: None | list[list[str]]


class AreaJSON(TypedDict):
    area_id: str
    area_name: str
    default_entrance: str
    exits: list[ExitJSON]


if TYPE_CHECKING:
    from typing import Literal

    from typing_extensions import TypeAlias

    TransitionInfosJSON: TypeAlias = dict[  # pyright: ignore  # Safe inside TYPE_CHECKING
        Literal[
            "Jungle",
            "Native Territory",
            "Lost Caverns",
            "Snowy Mountains",
        ],
        list[AreaJSON],  # pyright: ignore  # Safe inside TYPE_CHECKING
    ]
else:
    TransitionInfosJSON = None


@dataclass
class Exit:
    area_id: int
    area_name: str
    requires: None | list[list[str]]


@dataclass
class Area:
    area_id: int
    small_id: int
    name: str
    default_entrance: int
    exits: list[Exit]
    con_left: int


class MajorAreas(NamedTuple):
    jungle: list[Area]
    native_territory: list[Area]
    lost_caverns: list[Area]
    snowy_mountains: list[Area]
    spirit_fights: list[Area]
    el_dorado: list[Area]
    native_games: list[Area]
    cutscenes: list[Area]
    unused: list[Area]


def major_areas_from_JSON(transition_infos_json: TransitionInfosJSON):  # noqa: N802
    major_areas = [
        [
            Area(
                int(area["area_id"], 16),
                0,
                area["area_name"],
                int(area["default_entrance"] or "0x0", 16),
                [
                    Exit(
                        int(exit_["area_id"] or "0x0", 16),
                        exit_["area_name"],
                        exit_["requires"],
                    )
                    for exit_ in area["exits"]
                ],
                0
            )
            for area in major_area
        ]
        for major_area in transition_infos_json.values()
    ]
    counter = 1
    for major_area in major_areas:
        for area in major_area:
            area.con_left = len(area.exits)
            area.small_id = counter
            counter += 1
    return MajorAreas(*major_areas)


try:
    with Path.open(
        Path(__file__).parent / "transition_infos.json",
        encoding="UTF-8",
    ) as json_data:
        data: TransitionInfosJSON = json.load(json_data)
except FileNotFoundError as error:
    print(error, "Looking in 'Various technical notes' instead")
    with Path.open(
        Path(__file__).parent.parent.parent.parent
        / "Various technical notes"
        / "transition_infos.json",
        encoding="UTF-8",
    ) as json_data:
        data: TransitionInfosJSON = json.load(json_data)
# We don't wanna expose comments
del data["//"]  # pyright: ignore[reportArgumentType]


transition_infos = major_areas_from_JSON(data)
