# Dolphin Memory Watches (DMW)

Dolphin Memory Engine (DME) documentation: <https://github.com/aldelaro5/Dolphin-memory-engine>

To use, download the `.dmw` file for your game version (US, FR, etc.). Open Dolphin. Open DME. In DME, go under "File > Open..." and select the `.dmw` file you downloaded.

## Action Replay Codes

<!--
Finally found a guide that seems pretty complete for Action Replay codes.
It even explains how to deal with dynamic pointers, which is my current issue with Infinite Jump: https://www.reddit.com/r/learnprogramming/comments/6kqbcr/making_an_action_replay_code/
-->

All codes below are for NTSC Gamecube only

Start in specific Level (by Avasam):\
Replace `XXXX XXXX` by the `asset_crc32` found in [world_infos.json](/Various%20technical%20notes/world_infos.json)

```txt
0216A136 0000XXXX
0216A13E 0000XXXX
```

16:9 Aspect Ratio (by Avasam):

```txt
043D75E0 3FE38E39
```

Effectors Debug View (by DaveUltra+Avasam):

```txt
044CBAF4 00000001
```

## Gecko Codes

```txt
$16:9 Aspect Ratio [Avasam]
043D75E0 3FE38E39
*Sets the in-game camera's aspect ratio to 16:9
```

```txt
$Infinite Jumps [Avasam]
48000000 8041BE4C
DE000000 80008180
14000120 00000001
E0000000 80008000
*Freezes Harry's "Is Grounded" flag to 1. Only works for the standing state, not rolling or rafting.
```

```txt
$Debug: UFO Camera on Z+Start [Avasam]
040C45FC 480051ED
040C4600 48000028
042012B8 38800004
*Hold Z and press Start to toggle a free camera, Harry stays put.
*Main stick rotates, L switches it to panning and back.
*D-Pad pans, A/B/X/Y move, Z speeds up, R slows down.
*Replaces the removed debug menu's button, so enable only one "on Z+Start" code.
```

```txt
$Debug: Depth Complexity View on Z+Start [Avasam]
040C45FC 48004E9D
040C4600 48000028
*Hold Z and press Start to toggle an overdraw view: the scene drawn as green see-through layers, brighter where more surfaces overlap. Enable only one "on Z+Start" code.
```

```txt
$Debug: INV DEBUG Pause Menu Page [Avasam]
044CB974 00000001
*Adds the INV DEBUG page to the pause menu. It lets you pick the item on each D-pad direction, and unlock all six Heroic Moves at any time.
```

Other PTLE GC codes I found (not mines): <https://etherealgames.com/gcn/p/pitfall-the-lost-expedition/action-replay-codes-us/>
(TODO: Copy here, and/or even to official Dolphin AR codes?)
