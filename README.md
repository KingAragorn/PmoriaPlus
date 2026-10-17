# PmoriaPlus

PmoriaPlus is a free, non-commercial build of **Pmoria 0.98**, Christopher J. Petit's modification of Umoria 5.5.0. It keeps Pmoria's races, classes, spells, items, and commands, and it builds on current macOS and Linux with ncurses.

This project will not be sold. It is not relicensed. The copyright notices in the source are the license.

## License

Pmoria is Umoria 5.5 with Petit's additions. Umoria carries this notice from James E. Wilson and Robert A. Koeneke, which is preserved in the sources:

> Copyright (c) 1989-92 James E. Wilson, Robert A. Koeneke
>
> This software may be copied and distributed for educational, research, and not for profit purposes provided that this copyright and statement are included in all such copies.

`source/main.c` also keeps Koeneke's original dedication, including the condition that nobody may sell or market the software without his written consent. PmoriaPlus is distributed only as a free hobby project. Do not relicense it as the GPL, and do not drop these notices.

## Races and classes

Pmoria replaces the Umoria gnome with the Spectre and adds three races: Avion, Sage Elf, and Spectre. The new classes are Demigod, Sage, Jester, Ninja, Healer, Wizard, and Monk. Which classes a race may take is unchanged from `source/player.c`.

## Build

You need a C compiler, CMake 3.10 or newer, and ncurses development headers.

Debian or Ubuntu:

```sh
sudo apt install build-essential cmake libncurses-dev
```

macOS (Homebrew):

```sh
brew install cmake ncurses
```

Then:

```sh
cmake -S . -B build
cmake --build build
./build/pmoria
```

The binary looks for `files/hours`, the news file, and the help files in this order:

1. `$MORIA_LIB`, if that directory contains `hours`
2. the `files/` directory in this source tree
3. `../share/pmoria` next to the executable
4. the install prefix data directory (`share/pmoria`)

Install with:

```sh
cmake --install build
```

Scores are written to `$HOME/.pmoria/scores`, or to `$MORIA_SCORES` if that is set. Save files default to `$HOME/moria.save`.

## Terminal color

The dungeon map is drawn in color when the terminal supports it: walls, floors, doors, objects, and creatures each have a color, in the same spirit as later color Umoria ports. The character sheet and messages stay in the terminal's normal text.

Color is turned off, and the original monochrome curses output is used, when any of these is true:

- the terminal has no color
- you pass `-m`
- `MORIA_MONOCHROME` is set to anything other than `0`

```sh
./build/pmoria -m
MORIA_MONOCHROME=1 ./build/pmoria
```

Other startup flags are the original ones: `-n` ignores a save file, `-o` and `-r` choose the original or rogue-like key sets, `-s` and `-S` show scores, and `-w` requests wizard mode.

On macOS, if CMake does not find Homebrew's ncurses, configure with `CMAKE_PREFIX_PATH` set to the Homebrew prefix (`/opt/homebrew` or `/usr/local`).

## Smoke test

`scripts/smoke_characters.py` creates every legal race and class, walks a few steps in town, and saves:

```sh
python3 scripts/smoke_characters.py --binary build/pmoria
```

It needs the Python package `pyte`.

## Provenance

The first commit in this history is the unpacked `pmoria.tar.Z` from the Funet unofficial Moria source mirror (8 April 1993):

https://ftp.zx.net.nz/pub/mirror/ftp.funet.fi/pub/unix/games/moria/unofficial/source/pmoria.tar.Z

Petit's own notes are in `pmoria.mod`. The platform code (terminal setup, paths, signals, and the CMake build) is updated so the same game compiles with current ncurses. The game rules, tables, and text are the original Pmoria data.
