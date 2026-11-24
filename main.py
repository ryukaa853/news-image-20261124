#!/usr/bin/env python3
"""news-image-20261124 v1 -- one broadsheet image of Tuesday 24 November 2026.

Pure standard library only: a hand-rolled PNG writer, a monospace bitmap
font (generated from DejaVu Sans Mono on the build machine and embedded
below as row bitmasks), and a flow layout. Deterministic: no clock, no
randomness, no network. Writes entry.png to MAKEFUN_OUTPUT_DIR or /output.
"""

import os
import struct
import zlib

FONT = {
    ' ': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    'A': (24, 56, 40, 44, 100, 68, 70, 254, 194, 131, 387, 0, 0, 0),
    'B': (248, 204, 198, 196, 252, 252, 198, 194, 198, 196, 248, 0, 0, 0),
    'C': (60, 102, 64, 192, 192, 192, 192, 192, 192, 64, 102, 60, 0, 0),
    'D': (248, 204, 132, 134, 134, 134, 134, 134, 132, 204, 248, 0, 0, 0),
    'E': (254, 192, 192, 192, 252, 252, 192, 192, 192, 192, 254, 0, 0, 0),
    'F': (254, 192, 192, 192, 252, 252, 192, 192, 192, 192, 192, 0, 0, 0),
    'G': (60, 102, 64, 192, 192, 192, 206, 194, 194, 66, 102, 60, 0, 0),
    'H': (134, 134, 134, 130, 254, 254, 130, 134, 134, 134, 134, 0, 0, 0),
    'I': (254, 254, 24, 24, 24, 24, 24, 24, 24, 24, 254, 254, 0, 0),
    'J': (62, 6, 6, 6, 6, 6, 6, 6, 6, 204, 120, 0, 0, 0),
    'K': (256, 256, 384, 288, 480, 480, 432, 280, 392, 268, 262, 0, 0, 0),
    'L': (128, 128, 128, 128, 128, 128, 128, 128, 128, 192, 254, 0, 0, 0),
    'M': (390, 398, 462, 330, 306, 306, 306, 258, 258, 258, 258, 0, 0, 0),
    'N': (194, 194, 226, 162, 146, 146, 146, 138, 142, 134, 134, 0, 0, 0),
    'O': (120, 204, 132, 390, 390, 390, 390, 390, 390, 132, 204, 120, 0, 0),
    'P': (248, 204, 198, 198, 198, 252, 240, 192, 192, 192, 192, 0, 0, 0),
    'Q': (120, 204, 132, 390, 390, 390, 390, 390, 132, 204, 120, 24, 12, 0),
    'R': (496, 408, 396, 396, 392, 496, 408, 392, 396, 388, 390, 0, 0, 0),
    'S': (60, 100, 192, 128, 192, 120, 28, 6, 2, 6, 204, 120, 0, 0),
    'T': (510, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 0, 0, 0),
    'U': (198, 198, 198, 198, 198, 198, 198, 198, 198, 68, 56, 0, 0, 0),
    'V': (390, 388, 132, 132, 204, 72, 72, 72, 120, 48, 48, 0, 0, 0),
    'W': (257, 387, 387, 402, 178, 186, 170, 238, 238, 196, 68, 0, 0, 0),
    'X': (2, 70, 100, 40, 56, 16, 56, 108, 68, 198, 387, 0, 0, 0),
    'Y': (131, 194, 68, 108, 56, 24, 16, 16, 16, 16, 16, 0, 0, 0),
    'Z': (510, 4, 12, 24, 16, 48, 96, 64, 192, 384, 510, 0, 0, 0),
    'a': (0, 0, 0, 120, 70, 2, 62, 126, 194, 134, 206, 122, 0, 0),
    'b': (128, 128, 128, 248, 236, 196, 198, 134, 198, 196, 236, 184, 0, 0),
    'c': (0, 0, 0, 62, 98, 64, 192, 192, 192, 64, 96, 60, 0, 0),
    'd': (2, 2, 2, 62, 110, 198, 198, 194, 198, 70, 110, 58, 0, 0),
    'e': (0, 0, 0, 120, 204, 134, 390, 510, 384, 128, 196, 124, 0, 0),
    'f': (30, 16, 16, 254, 48, 16, 16, 16, 16, 16, 16, 0, 0, 0),
    'g': (0, 0, 0, 58, 110, 70, 198, 194, 198, 70, 126, 50, 6, 12),
    'h': (192, 192, 192, 252, 198, 198, 198, 198, 198, 198, 198, 0, 0, 0),
    'i': (0, 0, 24, 24, 0, 24, 24, 24, 24, 24, 24, 24, 0, 0),
    'j': (12, 0, 0, 60, 12, 12, 12, 12, 12, 12, 12, 12, 12, 120),
    'k': (128, 128, 128, 140, 152, 176, 240, 208, 136, 140, 132, 0, 0, 0),
    'l': (240, 48, 48, 48, 48, 48, 48, 48, 48, 16, 30, 0, 0, 0),
    'm': (0, 0, 0, 492, 438, 306, 306, 306, 306, 306, 306, 0, 0, 0),
    'n': (0, 0, 0, 156, 230, 198, 198, 198, 198, 198, 198, 0, 0, 0),
    'o': (0, 0, 0, 56, 108, 198, 134, 130, 134, 198, 108, 56, 0, 0),
    'p': (0, 0, 0, 184, 236, 198, 194, 194, 194, 198, 228, 248, 128, 192),
    'q': (0, 0, 0, 58, 110, 198, 198, 130, 194, 198, 110, 62, 2, 2),
    'r': (0, 0, 0, 188, 224, 192, 128, 128, 128, 128, 128, 0, 0, 0),
    's': (0, 0, 0, 120, 200, 128, 192, 120, 12, 12, 136, 248, 0, 0),
    't': (0, 48, 48, 254, 48, 48, 48, 48, 48, 48, 30, 0, 0, 0),
    'u': (0, 0, 0, 198, 198, 198, 198, 198, 198, 206, 122, 0, 0, 0),
    'v': (0, 0, 0, 390, 132, 132, 204, 72, 72, 48, 48, 0, 0, 0),
    'w': (0, 0, 0, 257, 387, 130, 146, 178, 238, 108, 68, 0, 0, 0),
    'x': (0, 0, 0, 0, 72, 120, 48, 48, 72, 204, 132, 0, 0, 0),
    'y': (0, 0, 0, 390, 132, 196, 76, 72, 120, 48, 48, 48, 96, 192),
    'z': (0, 0, 0, 254, 4, 12, 24, 48, 96, 64, 254, 0, 0, 0),
    '0': (56, 108, 196, 198, 198, 146, 146, 198, 198, 196, 108, 56, 0, 0),
    '1': (112, 208, 16, 16, 16, 16, 16, 16, 16, 24, 254, 0, 0, 0),
    '2': (120, 204, 6, 6, 4, 12, 24, 48, 96, 192, 254, 0, 0, 0),
    '3': (120, 204, 4, 6, 12, 56, 12, 6, 6, 6, 204, 248, 0, 0),
    '4': (24, 24, 40, 104, 72, 136, 392, 510, 28, 8, 8, 0, 0, 0),
    '5': (124, 64, 64, 64, 120, 4, 6, 6, 6, 140, 248, 0, 0, 0),
    '6': (60, 96, 64, 192, 152, 252, 198, 194, 194, 198, 108, 56, 0, 0),
    '7': (254, 4, 4, 12, 8, 8, 24, 16, 48, 32, 32, 0, 0, 0),
    '8': (56, 108, 198, 198, 68, 56, 68, 198, 130, 198, 108, 56, 0, 0),
    '9': (56, 76, 196, 134, 134, 198, 126, 50, 6, 4, 12, 120, 0, 0),
    '.': (0, 0, 0, 0, 0, 0, 0, 0, 0, 48, 48, 0, 0, 0),
    ',': (0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 24, 16, 48, 0),
    ':': (0, 0, 0, 48, 48, 0, 0, 0, 0, 48, 48, 0, 0, 0),
    ';': (0, 0, 0, 24, 24, 0, 0, 0, 0, 24, 24, 16, 48, 0),
    '!': (48, 48, 48, 48, 48, 48, 48, 0, 0, 48, 48, 0, 0, 0),
    '?': (120, 204, 12, 12, 24, 48, 32, 32, 0, 32, 32, 0, 0, 0),
    "'": (48, 48, 48, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    '"': (72, 72, 72, 72, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    '-': (0, 0, 0, 0, 0, 0, 120, 0, 0, 0, 0, 0, 0, 0),
    '/': (6, 4, 12, 8, 24, 16, 16, 32, 32, 96, 64, 192, 0, 0),
    '(': (24, 16, 48, 32, 32, 96, 96, 96, 32, 32, 48, 16, 24, 0),
    ')': (0, 16, 16, 24, 8, 8, 8, 8, 8, 24, 16, 16, 0, 0),
    '%': (192, 288, 292, 200, 16, 32, 70, 9, 9, 6, 0, 0, 0, 0),
    '$': (16, 124, 208, 144, 208, 120, 28, 22, 22, 252, 120, 16, 16, 0),
    '&': (56, 64, 192, 64, 96, 224, 147, 283, 270, 390, 206, 122, 0, 0),
    '+': (0, 0, 0, 48, 48, 48, 510, 48, 48, 48, 0, 0, 0, 0),
    '=': (0, 0, 0, 0, 510, 0, 0, 510, 0, 0, 0, 0, 0, 0),
    '<': (0, 0, 0, 6, 28, 240, 384, 240, 28, 6, 0, 0, 0, 0),
    '>': (0, 0, 0, 0, 224, 60, 6, 60, 224, 0, 0, 0, 0, 0),
    '@': (0, 60, 0, 129, 159, 307, 289, 289, 435, 159, 128, 96, 62, 0),
    '#': (18, 54, 36, 255, 108, 44, 108, 510, 72, 216, 144, 0, 0, 0),
    '*': (16, 16, 124, 56, 124, 16, 16, 0, 0, 0, 0, 0, 0, 0),
    '_': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 511),
    '—': (0, 0, 0, 0, 0, 0, 511, 0, 0, 0, 0, 0, 0, 0),
    '×': (0, 0, 0, 6, 4, 56, 48, 56, 4, 6, 0, 0, 0, 0),
    '·': (0, 0, 0, 0, 0, 48, 48, 0, 0, 0, 0, 0, 0, 0),
}

CELL_W, CELL_H = 9, 14

PAPER = (248, 245, 238)
INK = (20, 20, 20)
RED = (178, 34, 24)
NAVY = (20, 33, 61)
GREY = (96, 96, 96)
RULE = (198, 190, 174)
WHITE = (255, 255, 255)
LIGHT = (238, 233, 222)


def _chunk(typ, data):
    out = struct.pack('>I', len(data)) + typ + data
    out += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path, w, h, rgb):
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    raw = b''.join(b'\x00' + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))
    png = (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr)
           + _chunk(b'IDAT', zlib.compress(raw, 9)) + _chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)


def text_width(s, scale):
    return len(s) * CELL_W * scale


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines, cur = [], ''
    for word in text.split(' '):
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += ' ' + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def text(self, x, y, s, scale, color):
        for idx, ch in enumerate(s):
            rows = FONT.get(ch, FONT['?'])
            ox = x + idx * CELL_W * scale
            for r, bits in enumerate(rows):
                if not bits:
                    continue
                for c in range(CELL_W):
                    if (bits >> (CELL_W - 1 - c)) & 1:
                        bx, by = ox + c * scale, y + r * scale
                        for dy in range(scale):
                            for dx in range(scale):
                                self._set(bx + dx, by + dy, color)

    def text_centered(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def rule(self, x, y, w, color, thick=2):
        self.rect(x, y, w, thick, color)

W = H = 1024
M = 36  # margin
CW = W - 2 * M  # 952 content width


def build():
    c = Canvas(W, H, PAPER)

    # ---- Masthead ----
    c.rect(0, 0, W, 76, NAVY)
    c.text_centered(W // 2, 10, 'THE WORLD IN ONE DAY', 4, WHITE)
    c.text(M, 84, 'TUESDAY, 24 NOVEMBER 2026', 2, INK)
    right = 'make.fun'
    c.text(W - M - text_width(right, 2), 84, right, 2, INK)
    c.rule(0, 112, W, RED, 4)

    # ---- Lead: Nvidia ----
    y = 126
    c.text(M, y, 'TECH · MARKETS', 2, RED)
    y += 30
    for line in ['Nvidia soars 31%', 'as Huang returns']:
        c.text(M, y, line, 3, INK)
        y += 42
    y += 6
    lead_deck = ('Board reinstates its founder as chief after pressure '
                 'from Trump. S&P 500 jumps 4.7%, Nasdaq 6.5%.')
    for line in wrap(lead_deck, 34):
        c.text(M, y, line, 2, INK)
        y += 28
    lead_bottom = y
    # big number, right column
    c.text(680, 140, '+31%', 8, RED)
    c.text(680, 268, 'Nvidia shares', 2, INK)
    c.text(680, 296, 'in a day', 2, INK)

    y = max(lead_bottom, 330) + 14
    c.rule(M, y, CW, RULE, 2)
    y += 14

    # ---- Second story: Merkury ----
    c.text(M, y, 'UKRAINE · LIBYA', 2, RED)
    y += 30
    c.text(M, y, 'Kyiv sinks Russian warship off Libya', 2, INK)
    y += 30
    merk_deck = ('Seven naval drones sink the corvette Merkury at Benghazi. '
                 'Ukraine calls it self-defence.')
    for line in wrap(merk_deck, 52):
        c.text(M, y, line, 2, INK)
        y += 28
    y += 12
    c.rule(M, y, CW, RULE, 2)
    y += 16

    # ---- Grid: 3 cols x 2 rows ----
    stories = [
        ('CLIMATE', 'Climate talks end with no deal',
         'COP31 ends with no deal over fossil fuels.'),
        ('UKRAINE', 'Two killed in strike on flats',
         'Strike on flats kills 2, injures 22 overnight.'),
        ('IRAN · ENERGY', 'Tankers hit mines in Hormuz',
         'Iran says three tankers hit mines.'),
        ('GAZA', 'Strikes kill six in Gaza',
         'Strikes kill six, two of them police.'),
        ('IRAQ', 'Baghdad seizes Kurdish oilfields',
         'Baghdad seizes Kurdish oilfields.'),
        ('DR CONGO', 'Ebola teams trapped by fighting',
         'Fighting traps Ebola teams near Ituri hospital.'),
    ]
    col_w, gap = 304, 16
    xs = [M, M + col_w + gap, M + 2 * (col_w + gap)]
    grid_top = y
    # pre-wrap every cell
    cells = []
    for kicker, head, deck in stories:
        cells.append((kicker, wrap(head, 16), wrap(deck, 16)))
    row_h = []
    for r in range(2):
        h = 0
        for col in range(3):
            _, hl, dl = cells[r * 3 + col]
            h = max(h, 14 + 6 + len(hl) * 28 + 6 + len(dl) * 28)
        row_h.append(h)
    for r in range(2):
        cy = grid_top + sum(row_h[:r]) + r * 14
        for col in range(3):
            kicker, hl, dl = cells[r * 3 + col]
            cx = xs[col]
            c.text(cx, cy, kicker, 1, RED)
            yy = cy + 20
            for line in hl:
                c.text(cx, yy, line, 2, INK)
                yy += 28
            yy += 4
            for line in dl:
                c.text(cx, yy, line, 2, GREY)
                yy += 28
    y = grid_top + sum(row_h) + 14 + 10

    # ---- Also today ----
    c.text(M, y, 'ALSO TODAY', 2, RED)
    y += 30
    also = [
        'Indonesia factory fire kills 26',
        'Nepal quake, magnitude 5.6',
        'Car bomb in Villavicencio',
        "Mexico to try 'Chapo Isidro'",
        'Democrats take US House',
        'Pakistani to fly on Tiangong',
    ]
    for i, item in enumerate(also):
        ax = xs[i % 3]
        ay = y + (i // 3) * 18
        c.text(ax, ay, item, 1, INK)
    y += 2 * 18 + 12

    # ---- Markets footer ----
    c.rect(0, y, W, H - y, INK)
    foot = ('MARKETS  S&P 500 7,237 +4.73%  NASDAQ 24,090 +6.51%  '
            'NIKKEI 58,645 +3.91%  BRENT $86.71  GOLD $3,620')
    c.text_centered(W // 2, y + (H - y - 14) // 2, foot, 1, WHITE)
    return c


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    canvas = build()
    write_png(os.path.join(outdir, 'entry.png'), W, H, bytes(canvas.px))


if __name__ == '__main__':
    main()
