# Changelog

All notable changes to the Entrance Randomizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). The version semantics are inspired by [Semantic Versioning](https://semver.org/spec/v2.0.0.html). and go as follow:

```txt
Major.Minor.Patch

Major: New major feature or functionality (stays 0 until the first "stable" release)
Minor: Affects seed
Patch: Does't affect seed (assuming same settings)
```

This project uses [*towncrier*](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in [newsfragments](./newsfragments).

To add a changelog entry, add a new file `<issue_or_pr_#>.<type>.md` to the `newsfragments` folder.
(See the different [fragment types](https://towncrier.readthedocs.io/en/latest/tutorial.html#creating-news-fragments))

<!-- towncrier release notes start -->

## 0.4.0 - 2024-07-13

### Features

- - Add back crash site now that we can avoid the default entrance that resets progression
  - Added back teleporters as they're possibly fixed to activate when entering the right entrance
  - Add more info on-screen and in logs about entrances and unrandomized transitions

  -- by @Avasam ([#37](https://github.com/Avasam/ptle-tools/issues/37))
- - Guaranteed that if `CONFIGS.LINKED_TRANSITIONS == True` then all connections in the game are actually 2-way with the correct entrances
  - Added all four basic 1-way transitions (the geysers for instance) to the randomization process and made them randomized as well
  - Added Algorithm that guarantees that if `CONFIGS.LINKED_TRANSITIONS == True` then all levels are linked together in 1 big map, preventing any levels from being disconnected from the rest and therefore becoming unreachable
  - Updated transition_infos.json to include all levels in the entire game (even the one's we're not randomizing yet)
  - Updated list of levels we do NOT want to randomly pick as our starting_area

  -- by @wossnameGitHub ([#40](https://github.com/Avasam/ptle-tools/issues/40))
- Add graph of connections in `.graphml` format -- by @wossnameGitHub ([#42](https://github.com/Avasam/ptle-tools/issues/42))
- Added option to keep Jag1 & Jag2, or to skip jaguar fights entirely -- by @wossnameGitHub ([#45](https://github.com/Avasam/ptle-tools/issues/45))
- - No longer spoiling the start area in the UI as it doesn't affect randomization anymore
  - Added anti-softlock from missing items in Apu Illapu Shrine (Spinjas) and Scorpion Temple
  - Prevent starting area being a cutscene, Native Minigame, or Twin Outpost

  -- by @Avasam ([#49](https://github.com/Avasam/ptle-tools/issues/49))

### Bugfixes

- - Added anti-softlock from running into closed doors by bumping Harry's height in certain entrances
  - Fix `global _shaman_shop_prices` error

  -- by @Avasam ([#37](https://github.com/Avasam/ptle-tools/issues/37))
  - Fix altar of ages not being accessible (made rando impossible)
  - Fix non-existant transitions in list (could lead to impossible seed)

  -- by @wossnameGitHub ([#37](https://github.com/Avasam/ptle-tools/issues/37))
- - St. Claire's Camp bugfix (now Day & Night works properly, and the Rando is now proven to be fully functional New Game until Credits)
  - added 2 missing transitions (Twin Outposts -> Turtle Monument & Crystal Cavern -> Abandoned Cavern)

  -- by @wossnameGitHub ([#40](https://github.com/Avasam/ptle-tools/issues/40))
- Improve starting area randomization:

  - Manual vs random starting area won't affect the seed
  - Remove more unwanted starting areas possibilities

  -- by @wossnameGitHub ([#47](https://github.com/Avasam/ptle-tools/issues/47))

### Improved Documentation

- Improve various texts:

  - Fixed displaying non-random starting area
  - Changed how transition mapping is written in spoiler logs
  - Added rando features and more known issues to the readme
  - Fixed a few typos

   -- by @Avasam & @wossnameGitHub ([#46](https://github.com/Avasam/ptle-tools/issues/46))

### Deprecations and Removals

- Temporarily removed 3 levels from the rando pool (Scorpion Temple (Harry), Mouth of Inti, Twin Outposts (Underwater)) -- by @wossnameGitHub ([#40](https://github.com/Avasam/ptle-tools/issues/40))
- No longer spoiling the start area in the UI as it doesn't affect randomization anymore -- by @Avasam ([#49](https://github.com/Avasam/ptle-tools/issues/49))

### Misc

- [#43](https://github.com/Avasam/ptle-tools/issues/43)

## 0.3.0 - 2023-03-17

- Now comes with a readme! <https://github.com/Avasam/ptle-tools/tree/main/Dolphin%20scripts#entrance-randomizer-prototype>
- Linked transitions should now be a thing, although: "Non-vanilla transitions will always spawn Harry at the default entrance. This can be a bit confusing when using linked transitions."
- Crash Site and Teleports have been taken out of randomization (even if I could randomize at least the exits in non-linked transitions, I decided it's easier for now to just keep them vanilla)
- The Altar of Ages shortcut back to BBCamp after the cutscene from the first visit has been disabled. This standardizes exits.
- St. Claire's Excavation Camp Day and Night are now considered the same map for the Randomizer. And visiting Altar of Ages to get night camp is now enforced.
- Removed St. Claire's Excavation Camp, Apu Illapu Shrine (aka Spinjas) and Scorpion Temple from possible random starting areas (avoids immediate impossible seeds and getting TNT as your first area).
- Added Spoiler logs! (should be under dolphin-scripting-preview2/User/Logs, check Dolphin logs to see the exact location). You can now validate the seed is even possible. If a transition isn't listed in the spoiler log, it's vanilla.

Other than that, still no logic, this prototype is still mainly focused on exploring possibilities, finding issues and edgecases.
