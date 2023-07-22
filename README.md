<!-- markdownlint-disable MD033 -->

# PTLE Tools

A mono-repo and git sub-modules for all tools relating to Pitfall: The Lost Expedition (and The Big Adventure)

<br/>

## Dolphin

Download: <https://dolphin-emu.org/download/> (anything 5.0-14514 or above is fine)

Free Look: https://wiki.dolphin-emu.org/index.php?title=Free_Look

### Memory Watches (DMW)

Watch and modify useful memory regions. Basically practice tools.

Dolphin Memory Engine (DME): <https://github.com/aldelaro5/Dolphin-memory-engine/releases>\
Tables: [/Dolphin Memory Watches (DMW)](/Dolphin%20Memory%20Watches%20(DMW))

### Graphics Mods

Various graphical modifications and post-processing effects using [Dolphin's Graphics Mods](https://wiki.dolphin-emu.org/index.php?title=Graphics_Mods)

- [Clear HUD](https://github.com/Avasam/ptle-tools/tree/main/Graphics%20Mods#clear-hud)

### Texture Packs & Resource Packs

Read more about [Dolphin Custom Texure Projects](https://forums.dolphin-emu.org/Thread-how-to-install-texture-packs-custom-textures-info).

- [PC to Dolphin Texture Pack generator](/Texture%20packs/Dolphin%20PC%20texture%20pack%20generator)
- [Dynamic Input Pack](https://github.com/Avasam/UniversalDynamicInput/releases/latest) (display non-GameCube/Wii controller buttons)

### Entrance Randomizer

An entrance randomizer prototype using python scripting with Dolphin. See [/Dolphin scripts](/Dolphin%20scripts) for all the details.

<br/>

## Assets extraction

### Pitfall ARC Tool

Unarchive and re-archive `.arc` gamefiles.

Repository: <https://github.com/UltiNaruto/PitfallARCTool>

### TexConvert

A tool to convert unarchived Pitfall TXFL/LFXT format textures **from any console or version** into different usable formats.

Releases: <https://github.com/Helco/Pitfall/releases>

### DolphinTextureExtraction-tool

Dumps GameCube and Wii textures to a format and name compatible with Dolphin texture hash.

Repository: <https://github.com/Venomalia/DolphinTextureExtraction-tool#readme>

<br/>

## AutoSplitter

A memory-based LiveSplit AutoSplitter for the PC version. Automatically installed with LiveSplit.

Read more: <https://github.com/Avasam/Avasam.AutoSplitters/tree/main/Pitfall%20The%20Lost%20Expedition>

<br/>

## Meta / Contributing

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Avasam/ptle-tools/main.svg)](https://results.pre-commit.ci/latest/github/Avasam/ptle-tools/main)

### Formatting, linting and type-checking

You can simply install [pre-commit](https://pre-commit.ci/) (`pip install pre-commit`) and run it (`pre-commit run`) to lint, type-check, and automatically format all files.

Autofixable issues will automatically be resolved when creating a pull-request.

#### Format on save

To automatically format on save using the Visual Studio Code editor, make sure to install all recommended extensions in [.vscode/extensions.json](.vscode/extensions.json). You should also [install dprint](https://dprint.dev/install/) and our python dev dependencies (`pip install -r ".\Dolphin scripts\requirements-dev.txt"`)
