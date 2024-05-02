<!-- markdownlint-disable MD033 -->

# PTLE Tools

A mono-repo and git sub-modules for all tools relating to Pitfall: The Lost Expedition (and The Big Adventure)

<br/>

## Dolphin

Download: <https://dolphin-emu.org/download/> (anything 5.0-14514 or above is fine)

Free Look: <https://wiki.dolphin-emu.org/index.php?title=Free_Look>

### Memory Watches (DMW)

Watch and modify useful memory regions. Basically practice tools.

Dolphin Memory Engine (DME): <https://github.com/aldelaro5/Dolphin-memory-engine/releases>\
Tables: [/Dolphin Memory Watches (DMW)](/Dolphin%20Memory%20Watches%20(DMW))

### Graphics Mods

Various graphical modifications and post-processing effects using [Dolphin's Graphics Mods](https://wiki.dolphin-emu.org/index.php?title=Graphics_Mods)

- [Clear HUD](https://github.com/Avasam/ptle-tools/tree/main/Graphics%20Mods#clear-hud)

### Texture Packs & Resource Packs

Read more about [Dolphin Custom Texure Projects](https://forums.dolphin-emu.org/Thread-how-to-install-texture-packs-custom-textures-info).

- [PC to Dolphin Texture Pack generator](/Texture%20packs/Dolphin%20PC%20texture%20pack%20generator) (higher resolution textures from the PC version)
- [Supai Restored](https://chris1111.github.io/DownGit/#/home?url=https://github.com/Avasam/ptle-tools/tree/main/Texture%20packs/PTLE-Supai-Restored)\
  ![](/Texture%20packs/PTLE-Supai-Restored/logo.png)
  - Restores Supai to its non-demonic form. This uses altered PC textures.
    - The body had to be vertically flipped.
    - The head required manual adjustments to align the texture elements.
    - Flames, body sheen, and eye glow removed.
- [Dynamic Input Pack](https://github.com/Venomalia/UniversalDynamicInput#how-to-install-the-pack) (display non-GameCube/Wii controller buttons)
  \
  Download: <https://github.com/Venomalia/UniversalDynamicInput/releases/latest>\
  |![Controls Remap](https://user-images.githubusercontent.com/1350584/233196583-abc829b4-59cd-4f86-bb2c-26b3e6fb7d7f.png)|![Looking Around](https://user-images.githubusercontent.com/1350584/233196608-ce722296-8a88-4634-a08c-ce6dca7712c2.png)|![Switches](https://user-images.githubusercontent.com/1350584/233196610-30e426d7-6a2d-4426-96d5-4151567d2981.png)|![Vine Climbing](https://user-images.githubusercontent.com/1350584/233196611-861ceda7-8670-45dc-a52b-72e3cd40aca3.png)
  |-|-|-|-|
  |![Vine Steering](https://user-images.githubusercontent.com/1350584/233196612-fe30350b-ed69-43de-bedc-f8d842240714.png)|![Camera](https://user-images.githubusercontent.com/1350584/233196615-7aae3a68-9daf-45ae-a17f-a42ad4082411.png)|![Items](https://user-images.githubusercontent.com/1350584/233196617-4bc996d4-06f3-4301-a813-e6ceac37167b.png)|![Super Sling](https://user-images.githubusercontent.com/1350584/233208007-9eb4379a-8e35-4cd4-bbbd-2660965decb5.png)

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
[![PTLE Discord](https://badgen.net/discord/members/NEVJPZk)](https://discord.gg/NEVJPZk)

### Formatting, linting and type-checking

You can simply install [pre-commit](https://pre-commit.ci/) (`pip install pre-commit`) and run it (`pre-commit run`) to lint, type-check, and automatically format all files.

Autofixable issues will automatically be resolved when creating a pull-request.

#### Format on save

To automatically format on save using the Visual Studio Code editor, make sure to install all recommended extensions in [.vscode/extensions.json](.vscode/extensions.json). You should also [install dprint](https://dprint.dev/install/) and our python dev dependencies (`pip install -r ".\Dolphin scripts\requirements-dev.txt"`)
