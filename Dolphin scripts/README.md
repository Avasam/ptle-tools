# Using Python scripts with Dolphin

1. Use this fork of Dolphin <https://github.com/Felk/dolphin/releases>.
2. Turn on "Scripting" logs and set Verbosity to "Error" or any option below (not "Notice").
3. Under "Scripts", click "Add new Scripts" and select your Python script.

## Entrance Randomizer

### Features
- Randomization of almost all basic transitions in the game
- Randomization of Shaman Shop prices
- Generation of Spoiler Log `.txt` file
- Generation of Randomized Map `.graphml` file
- Option to manually choose a seed, or to get a random seed
- Option to manually choose a starting area, or to get a random starting area
- Option to make all transitions 2-directional, or to allow 1-directional transitions
- Option to skip both Jaguar fights entirely, or to keep them as normal
- Option to disable maps from the Shaman Shop, or to let them remain
- Further options for Shaman Shop prices

### Installing

1. Use this fork of Dolphin <https://github.com/Felk/dolphin/releases>.
2. Turn on "Scripting" logs and set Verbosity to "Error" or any option below (not "Notice").
3. Download the zip file from Discord or zip it yourself using `pack-rando.ps1`.
4. Open this zip file and drop "Scripts" at the root of your Dolphin installation (the location and names are important!).
5. Configurations are found in `Scripts/Entrance Randomizer/CONFIGS.py`.
6. In Dolphin, under "Scripts", click "Add new Scripts" and select `Scripts/Entrance Randomizer/__main__.py`.
7. Enjoy and watch logs for errors 🙂

### About the .graphml file

In order to display the generated map take these steps:
1. Go to https://graphonline.ru/en/
2. Under "Graph" choose "Import from file" and choose your generated `.graphml` file
3. Under "Algorithms" choose "Arrange the graph"
4. Enjoy your map! You can freely move the dots, and you can use multiple features under the "Algorithms" tab (like "Find all paths" for instance)
5. You can also save your map at any time by choosing "Graph" --> "Export to file"

### Known issues and limitations

- To generate a new seed, simply reload the script
- Sometimes a transition does not make you enter the level from the correct entrance, but from the default entrance instead
- Some seeds will result in impossible to complete configurations, because you might need some items to progress that you don't have yet
- When using `LINKED_TRANSITIONS = False` the generated `.graphml` map will become very hard to read, given the extreme amount of connections that will be drawn

### Developing

1. Use this fork of Dolphin <https://github.com/Felk/dolphin/releases>.
2. Turn on "Scripting" logs and set Verbosity to "Error" or any option below (not "Notice").
3. Clone this repository
4. Run `symlink-scripts.ps1 "<path to dolphin-scripting>"`
5. In Dolphin, under "Scripts", click "Add new Scripts" and select `Scripts/Entrance Randomizer/__main__.py`.
