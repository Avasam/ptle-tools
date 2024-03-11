# Dolphin Memory Watches (DMW)

Dolphin Memory Engine (DME) documentation: <https://github.com/aldelaro5/Dolphin-memory-engine>

To use, download the `.dmw` file for your game version (US, FR, etc.). Open Dolphin. Open DME. In DME, go under "File > Open..." and select the `.dmw` file you downloaded.

## Action Replay / Gecko Codes

<!--
Finally found a guide that seems pretty complete for Action Replay codes.
It even explains how to deal with dynamic pointers, which is my current issue with Infinite Jump: https://www.reddit.com/r/learnprogramming/comments/6kqbcr/making_an_action_replay_code/
-->

All codes below are for NTSC Gamecube only

Start in specific Level (by Avasam):  
Replace `XXXX XXXX` by the `asset_crc32` found in [world_infos.json](/Various%20technical%20notes/world_infos.json)

```txt
0216A136 0000XXXX
0216A13E 0000XXXX
```

_**The codes below are a bit jank because they don't follow pointers and can randomly break**_

Infinite Jumps (by Avasam):

```txt
00969A63 00000001
0096A0B3 00000001
0097A0D3 00000001
```

Infinite Idols (by Avasam):

```txt
04832ECC 000000FF
04835EE4 000000FF
04836A9C 000000FF
```

Other PTLE GC codes I found (not mines): <https://etherealgames.com/gcn/p/pitfall-the-lost-expedition/action-replay-codes-us/>
(TODO: Copy here, and/or even to official Dolphin AR codes?)
