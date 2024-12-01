import re
import sys
from os import listdir
from pathlib import Path

NEWS_TYPES = ("feature", "bugfix", "doc", "removal", "misc")
NEWS_PATTERN = re.compile(r"(\d+|\+.+)\.(" + "|".join(NEWS_TYPES) + r")\.md")
NEWSFRAGMENTS_FIR = (
    Path(__file__).parent.parent
    / "Dolphin scripts"
    / "Entrance Randomizer"
    / "newsfragments"
)


def main():
    invalid_filenames = [
        filename for filename
        in listdir(NEWSFRAGMENTS_FIR)  # noqa: PTH208 # Easier as strings
        if not (NEWS_PATTERN.fullmatch(filename) or filename.endswith(".gitignore"))
    ]

    if invalid_filenames:
        sys.exit(
            "The following newsfragments don't match the "
            + f"{NEWS_PATTERN} pattern: {invalid_filenames}",
        )


if __name__ == "__main__":
    main()
