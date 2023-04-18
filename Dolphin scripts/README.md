# Using Python scripts with Dolphin

1. Use this fork of Dolphin <https://github.com/Felk/dolphin/releases>.
2. Turn on "Scripting" logs and set Verbosity to "Error" or any option below (not "Notice").
3. Under "Scripts", click "Add new Scripts" and select your Python script.

## Entrance Randomizer (prototype)

### Installing

1. Use this fork of Dolphin <https://github.com/Felk/dolphin/releases>.
2. Turn on "Scripting" logs and set Verbosity to "Error" or any option below (not "Notice").
3. Download the zip file from Discord or zip it yourself using `pack-rando.ps1`.
4. Open this zip file and drop "Scripts" at the root of your Dolphin installation (the location and names are important!).
5. Configurations are found in `Scripts/Entrance Randomizer/CONFIGS.py`.
6. In Dolphin, under "Scripts", click "Add new Scripts" and select `Scripts/Entrance Randomizer/__main__.py`.
7. Enjoy and watch logs for errors 🙂

### Known issues and limitations

- To generate a new seed, simply reload the script.
- Non-vanilla transitions will always spawn Harry at the default entrance. This can be a bit confusing when using linked transitions.
- Some areas are not randomized because they are broken with default transition. These can be fixed eventually:
  - Crash Site: Removes all abilities and items
  - Teleport: The teleporter pads only activate based on which (vanilla) transition was taken.

### Developing

1. Use this fork of Dolphin <https://github.com/Felk/dolphin/releases>.
2. Turn on "Scripting" logs and set Verbosity to "Error" or any option below (not "Notice").
3. Clone this repository
4. Run `symlink-scripts.ps1 "<path to dolphin-scripting>"`
5. In Dolphin, under "Scripts", click "Add new Scripts" and select `Scripts/Entrance Randomizer/__main__.py`.
