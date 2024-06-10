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


@dataclass(frozen=True)
class Exit:
    area_id: int
    area_name: str
    requires: None | list[list[str]]


@dataclass(frozen=False)  # TODO: Change code that mutates this and change this back to True
class Area:
    area_id: int
    name: str
    default_entrance: int
    exits: tuple[Exit, ...]
    con_left: int


class MajorAreas(NamedTuple):
    jungle: tuple[Area, ...]
    native_territory: tuple[Area, ...]
    lost_caverns: tuple[Area, ...]
    snowy_mountains: tuple[Area, ...]
    spirit_fights: tuple[Area, ...]
    el_dorado: tuple[Area, ...]
    native_games: tuple[Area, ...]
    cutscenes: tuple[Area, ...]
    unused: tuple[Area, ...]


def major_areas_from_JSON(transition_infos_json: TransitionInfosJSON):  # noqa: N802
    major_areas = [
        tuple(
            Area(
                int(area["area_id"], 16),
                area["area_name"],
                int(area["default_entrance"] or "0x0", 16),
                tuple(
                    Exit(
                        int(exit_["area_id"] or "0x0", 16),
                        exit_["area_name"],
                        exit_["requires"],
                    )
                    for exit_ in area["exits"]
                ),
                len(area["exits"]),
            )
            for area in major_area
        )
        for major_area in transition_infos_json.values()
    ]
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
