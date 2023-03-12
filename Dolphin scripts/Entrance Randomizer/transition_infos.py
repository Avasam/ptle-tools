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

    TransitionInfosJSON: TypeAlias = dict[
        Literal[
            "Jungle",
            "Native Territory",
            "Lost Caverns",
            "Snowy Mountains",
        ],
        list[AreaJSON],
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
    name: str
    default_entrance: int
    exits: list[Exit]


class MajorAreas(NamedTuple):
    jungle: list[Area]
    native_territory: list[Area]
    lost_caverns: list[Area]
    snowy_mountains: list[Area]


def major_areas_from_JSON(transition_infos_json: TransitionInfosJSON):
    major_areas = [
        [
            Area(
                int(area["area_id"], 16),
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
            )
            for area in major_area
        ]
        for major_area in transition_infos_json.values()
    ]
    return MajorAreas(*major_areas)


try:
    with open(
        Path(__file__).parent / "transition_infos.json",
        encoding="UTF-8",
    ) as json_data:
        data: TransitionInfosJSON = json.load(json_data)
except FileNotFoundError as error:
    print(error, "Looking in 'Various technical notes' instead")
    with open(
        Path(__file__).parent.parent.parent
        / "Various technical notes"
        / "transition_infos.json",
        encoding="UTF-8",
    ) as json_data:
        data: TransitionInfosJSON = json.load(json_data)
# We don't wanna expose comments
del data["//"]  # type: ignore[reportGeneralTypeIssues]


transition_infos = major_areas_from_JSON(data)
