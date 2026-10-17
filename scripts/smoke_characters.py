#!/usr/bin/env python3
"""Create every legal Pmoria race/class and play a few turns.

Drives ./build/pmoria on a pseudoterminal. Exits non-zero if any combo
fails to reach the character sheet or the town map.
"""

import argparse
import fcntl
import os
import pty
import select
import struct
import subprocess
import sys
import termios
import time

import pyte

RACES = [
    ("Human", 0x1FFF),
    ("Half-Elf", 0x1FFF),
    ("Elf", 0x15CF),
    ("Halfling", 0x07CB),
    ("Spectre", 0x088D),
    ("Dwarf", 0x00C5),
    ("Half-Orc", 0x01CD),
    ("Half-Troll", 0x0145),
    ("Avion", 0x044F),
    ("Sage Elf", 0x17CF),
]
CLASSES = [
    "Warrior", "Mage", "Priest", "Rogue", "Ranger", "Paladin",
    "Demigod", "Sage", "Jester", "Ninja", "Healer", "Wizard", "Monk",
]

ROWS = 24
COLS = 80


def class_letter(mask, index):
    if not (mask & (1 << index)):
        return None
    seen = 0
    for bit in range(index):
        if mask & (1 << bit):
            seen += 1
    return chr(ord("a") + seen)


def legal_combos():
    for race_i, (race, mask) in enumerate(RACES):
        for class_i, title in enumerate(CLASSES):
            letter = class_letter(mask, class_i)
            if letter is not None:
                yield race_i, race, class_i, title, letter


class Session:
    def __init__(self, binary, home, monochrome=False):
        self.screen = pyte.Screen(COLS, ROWS)
        self.stream = pyte.Stream(self.screen)
        self.master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        env["ESCDELAY"] = "10"
        env["HOME"] = home
        env["COLUMNS"] = str(COLS)
        env["LINES"] = str(ROWS)
        if monochrome:
            env["MORIA_MONOCHROME"] = "1"
        else:
            env.pop("MORIA_MONOCHROME", None)
        self.proc = subprocess.Popen(
            [binary, "-n"],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            env=env,
            close_fds=True,
        )
        os.close(slave)

    def close(self):
        if self.proc.poll() is None:
            try:
                self.proc.kill()
            except OSError:
                pass
            self.proc.wait(timeout=2)
        try:
            os.close(self.master)
        except OSError:
            pass

    def text(self):
        return "\n".join(line.rstrip() for line in self.screen.display)

    def pump(self, timeout):
        end = time.time() + timeout
        while time.time() < end:
            ready, _, _ = select.select([self.master], [], [], 0.05)
            if self.master not in ready:
                if self.proc.poll() is not None:
                    return
                continue
            try:
                data = os.read(self.master, 65536)
            except OSError:
                return
            if not data:
                return
            self.stream.feed(data.decode("latin1", errors="replace"))

    def wait_for(self, needle, timeout=8):
        end = time.time() + timeout
        while time.time() < end:
            self.pump(0.1)
            if needle in self.text():
                return True
            if self.proc.poll() is not None:
                return False
        return needle in self.text()

    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
        os.write(self.master, data)
        time.sleep(0.02)


def clone_screen(screen):
    cloned = pyte.Screen(COLS, ROWS)
    for y in range(ROWS):
        for x in range(COLS):
            cell = screen.buffer[y][x]
            cloned.buffer[y][x] = pyte.screens.Char(
                data=cell.data, fg=cell.fg, bg=cell.bg,
                bold=cell.bold, italics=cell.italics,
                underscore=cell.underscore, strikethrough=cell.strikethrough,
                reverse=cell.reverse, blink=cell.blink,
            )
    return cloned


def render_png(screen, path):
    from PIL import Image, ImageDraw, ImageFont

    colors = {
        "black": (0, 0, 0),
        "red": (170, 0, 0),
        "green": (0, 170, 0),
        "yellow": (170, 140, 0),
        "brown": (170, 140, 0),
        "blue": (0, 0, 170),
        "magenta": (170, 0, 170),
        "cyan": (0, 170, 170),
        "white": (170, 170, 170),
        "brightblack": (85, 85, 85),
        "brightred": (255, 85, 85),
        "brightgreen": (85, 255, 85),
        "brightyellow": (255, 255, 85),
        "brightblue": (85, 85, 255),
        "brightmagenta": (255, 85, 255),
        "brightcyan": (85, 255, 255),
        "brightwhite": (255, 255, 255),
        "default": (170, 170, 170),
    }
    cell_w, cell_h = 9, 16
    image = Image.new("RGB", (COLS * cell_w, ROWS * cell_h), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14
    )
    for y in range(ROWS):
        for x in range(COLS):
            cell = screen.buffer[y][x]
            ch = cell.data or " "
            fg = colors.get(str(cell.fg).lower(), (170, 170, 170))
            if cell.bold and str(cell.fg).lower() in colors:
                bright = "bright" + str(cell.fg).lower()
                fg = colors.get(bright, fg)
            draw.text((x * cell_w, y * cell_h - 2), ch, font=font, fill=fg)
    image.save(path)


def play_combo(binary, home, race_i, race, class_title, class_key, shots):
    session = Session(binary, home)
    try:
        if not session.wait_for("Press any key to continue"):
            return False, "news screen did not appear", session
        session.send(" ")
        if not session.wait_for("Choose a race"):
            return False, "race prompt missing", session
        session.send(chr(ord("a") + race_i))
        if not session.wait_for("Choose a sex"):
            return False, "sex prompt missing", session
        session.send("m")
        if not session.wait_for("reroll"):
            return False, "stat prompt missing", session
        session.send("\033")
        if not session.wait_for("Choose a class"):
            return False, "class prompt missing", session
        session.send(class_key)
        if not session.wait_for("player's name"):
            return False, "name prompt missing", session
        session.send("\r")
        if not session.wait_for("or Q to exit"):
            return False, "character sheet did not finish", session
        lines = session.screen.display
        race_field = lines[3][15:].strip()
        class_field = lines[5][15:].strip()
        if not race_field.startswith(race) or not class_field.startswith(class_title):
            return False, "sheet shows %r / %r" % (race_field, class_field), session
        if shots is not None:
            shots["sheet_screen"] = pyte.Screen(COLS, ROWS)
            shots["sheet_screen"].buffer = session.screen.buffer
            # pyte Screen.buffer is live. Copy the rendered lines and colors
            # by cloning through the current display plus a deep copy below.
            shots["sheet"] = clone_screen(session.screen)
        session.send(" ")
        session.pump(0.5)
        # A few real turns, with spaces so a -more- prompt cannot swallow them.
        session.send(" h j k l h l ")
        session.pump(0.5)
        town = session.text()
        if "@" not in town and "Dead" not in town and "RIP" not in town:
            return False, "never reached the map", session
        if shots is not None:
            shots["play"] = clone_screen(session.screen)
        session.send("\x18")
        end = time.time() + 8
        while time.time() < end and session.proc.poll() is None:
            session.pump(0.15)
            text = session.text()
            if "Delete old savefile" in text:
                session.send("y")
            elif "-more-" in text or "Press any key" in text:
                session.send(" ")
        if session.proc.poll() is None:
            return False, "did not save and exit\n" + session.text(), session
        if session.proc.returncode not in (0, None) and session.proc.returncode < 0:
            return False, "killed by signal %s" % (-session.proc.returncode), session
        return True, town, None
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="build/pmoria")
    parser.add_argument("--home", default="")
    parser.add_argument("--shots", default="")
    parser.add_argument("--only", default="")
    args = parser.parse_args()
    binary = os.path.abspath(args.binary)
    home = args.home or os.path.join("/tmp", "pmoria-smoke-%d" % os.getpid())
    os.makedirs(home, exist_ok=True)
    failures = []
    combos = list(legal_combos())
    if args.only:
        race, title = args.only.split("/", 1)
        combos = [c for c in combos if c[1] == race and c[3] == title]
    print("playing %d race/class combinations" % len(combos))
    shot_target = ("Sage Elf", "Sage")
    for race_i, race, _class_i, title, letter in combos:
        want_shots = bool(args.shots) and (race, title) == shot_target
        shots = {} if want_shots else None
        ok, detail, _held = play_combo(
            binary, home, race_i, race, title, letter, shots
        )
        label = "%s %s" % (race, title)
        if ok:
            print("ok  %s" % label)
            if want_shots:
                os.makedirs(args.shots, exist_ok=True)
                render_png(shots["sheet"], os.path.join(args.shots, "character.png"))
                render_png(shots["play"], os.path.join(args.shots, "gameplay.png"))
                colored = 0
                for y in range(1, ROWS - 1):
                    for x in range(13, COLS):
                        fg = str(shots["play"].buffer[y][x].fg).lower()
                        if fg not in ("default", "white", "black", ""):
                            colored += 1
                print("colored map cells in gameplay shot: %d" % colored)
                if colored < 4:
                    failures.append((label, "gameplay shot has no terminal color"))
        else:
            failures.append((label, detail))
            print("FAIL %s: %s" % (label, detail))
            if isinstance(detail, str) and detail.startswith("sheet"):
                pass
    print("%d failures" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
