#!/usr/bin/env python3
"""Draw the World News infographic for Friday 20 November 2026.

Newspaper-style front page: a navy masthead with the date, one big lead
story (the historic Trump-Xi-Putin trilateral in Shenzhen), four more
story panels (markets, ICJ, Anthropic IPO, Cyclone Akvan), a bottom row
with two short stories (Iran, Voyager 1), and a footer ticker. Rendered
with Pillow only, no network. Output: entry.png, 1024x1024, under 1 MiB.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 244, 236)
NAVY = (18, 32, 56)
GOLD = (201, 162, 39)
INK = (24, 24, 24)
MUTED = (90, 86, 76)
WHITE = (255, 255, 255)
BORDER = (214, 208, 192)
LIGHT = (242, 239, 230)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_BOLD = FONT_DIR + "DejaVuSerif-Bold.ttf"
SERIF = FONT_DIR + "DejaVuSerif.ttf"
SANS_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def star_points(cx, cy, r_outer, r_inner, rotation=-90):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(rotation + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def panel(draw, x0, y0, x1, y1, accent):
    """White story panel with a thin border and a coloured top bar."""
    draw.rectangle([x0, y0, x1, y1], fill=WHITE, outline=BORDER, width=2)
    draw.rectangle([x0, y0, x1, y0 + 6], fill=accent)


def kicker(draw, x, y, text, color):
    draw.text((x, y), text, font=font(SANS_BOLD, 21), fill=color)


def headline(draw, x, y, text, fnt, max_w, leading=1.12):
    lines = wrap(draw, text, fnt, max_w)
    for i, line in enumerate(lines):
        draw.text((x, y + i * int(fnt.size * leading)), line, font=fnt, fill=INK)
    return y + len(lines) * int(fnt.size * leading)


def body(draw, x, y, text, max_w, size=23):
    fnt = font(SANS, size)
    for i, line in enumerate(wrap(draw, text, fnt, max_w)):
        draw.text((x, y + i * (size + 6)), line, font=fnt, fill=(52, 52, 52))
    return y + len(wrap(draw, text, fnt, max_w)) * (size + 6)


def roundel(base, cx, cy, r, kind):
    """A flag roundel: USA (navy + white star), CHINA (red + yellow star),
    RUSSIA (white/blue/red stripes). Drawn on its own tile, masked round."""
    tile = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    if kind == "usa":
        td.ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=(28, 52, 104, 255))
        td.polygon(star_points(r + 2, r + 2, r * 0.55, r * 0.23), fill=(255, 255, 255, 255))
    elif kind == "china":
        td.ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=(206, 32, 40, 255))
        td.polygon(star_points(r + 2, r + 2, r * 0.55, r * 0.23), fill=(255, 222, 0, 255))
    else:  # russia: horizontal stripes clipped to the circle
        mask = Image.new("L", (2 * r + 4, 2 * r + 4), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=255)
        stripes = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stripes)
        third = (2 * r + 4) / 3
        sd.rectangle([0, 0, 2 * r + 4, third], fill=(255, 255, 255, 255))
        sd.rectangle([0, third, 2 * r + 4, 2 * third], fill=(0, 84, 166, 255))
        sd.rectangle([0, 2 * third, 2 * r + 4, 2 * r + 4], fill=(213, 0, 50, 255))
        tile.paste(stripes, (0, 0), mask)
    base.paste(tile, (cx - r - 2, cy - r - 2), tile)
    d = ImageDraw.Draw(base)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 110, 90), width=2)


def fit_headline(draw, x, y, text, max_w, size=22):
    """Draw a headline on ONE line, shrinking the font until it fits.
    (The Voyager headline wrapped at 22px and its second line overlapped
    the subhead below, so row-4 headlines must never wrap.)"""
    fnt = font(SERIF_BOLD, size)
    while draw.textlength(text, font=fnt) > max_w and size > 14:
        size -= 1
        fnt = font(SERIF_BOLD, size)
    draw.text((x, y), text, font=fnt, fill=INK)
    return y + size


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------
    d.rectangle([0, 0, W, 132], fill=NAVY)
    title = "WORLD NEWS"
    tf = font(SERIF_BOLD, 66)
    d.text(((W - d.textlength(title, font=tf)) / 2, 16), title, font=tf, fill=WHITE)
    d.line([60, 100, W - 60, 100], fill=GOLD, width=3)
    date = "FRIDAY, 20 NOVEMBER 2026"
    df = font(SANS_BOLD, 28)
    d.text(((W - d.textlength(date, font=df)) / 2, 104), date, font=df, fill=GOLD)

    # ---- Lead story: Shenzhen trilateral --------------------------
    panel(d, 24, 148, 1000, 392, (43, 95, 138))
    kicker(d, 44, 166, "SHENZHEN  ·  HISTORIC FIRST", (43, 95, 138))
    y = headline(d, 44, 196, "TRUMP, XI AND PUTIN MEET",
                 font(SERIF_BOLD, 44), 600)
    body(d, 44, y + 10,
         "First-ever three-way summit ends with a peace declaration on "
         "nuclear risks. APEC adopts the Shenzhen Outlook on trade, data and AI.",
         600)
    # three flag roundels on the right
    for cx, kind, label in ((716, "usa", "USA"), (826, "china", "CHINA"),
                            (936, "russia", "RUSSIA")):
        roundel(img, cx, 252, 44, kind)
        lf = font(SANS_BOLD, 19)
        d.text((cx - d.textlength(label, font=lf) / 2, 304), label,
               font=lf, fill=MUTED)
    tag = "PEACE DECLARATION"
    tg = font(SANS_BOLD, 21)
    tw = d.textlength(tag, font=tg)
    d.rounded_rectangle([826 - tw / 2 - 14, 336, 826 + tw / 2 + 14, 370],
                        radius=8, fill=(242, 231, 196), outline=GOLD, width=2)
    d.text((826 - tw / 2, 341), tag, font=tg, fill=(122, 92, 12))

    # ---- Row 2: markets + ICJ -------------------------------------
    # Markets
    panel(d, 24, 408, 500, 636, (178, 34, 34))
    kicker(d, 44, 424, "WALL STREET", (178, 34, 34))
    y = headline(d, 44, 452, "MARKETS PLUNGE", font(SERIF_BOLD, 36), 440)
    # falling chart
    gx0, gy0, gx1, gy1 = 44, y + 12, 480, 566
    d.rectangle([gx0, gy0, gx1, gy1], fill=LIGHT, outline=BORDER, width=1)
    for i in range(1, 4):
        gy = gy0 + i * (gy1 - gy0) // 4
        d.line([gx0, gy, gx1, gy], fill=(226, 220, 206), width=1)
    pts = [(gx0 + 8, gy0 + 10), (gx0 + 70, gy0 + 22), (gx0 + 130, gy0 + 18),
           (gx0 + 190, gy0 + 44), (gx0 + 250, gy0 + 40), (gx0 + 310, gy0 + 66),
           (gx0 + 370, gy0 + 62), (gx1 - 8, gy1 - 12)]
    d.line(pts, fill=(178, 34, 34), width=5, joint="curve")
    d.polygon([(gx1 - 8, gy1 - 12), (gx1 - 26, gy1 - 26), (gx1 - 26, gy1 - 6)],
              fill=(178, 34, 34))
    # label sits in the empty bottom-left corner, clear of the falling line
    d.text((gx0 + 8, gy1 - 24), "DOW", font=font(SANS_BOLD, 18), fill=(178, 34, 34))
    body(d, 44, 578,
         "Dow -1,101 points to 49,097. S&P 500 -2.02%, Nasdaq -2.25%.",
         436, size=21)

    # ICJ
    panel(d, 524, 408, 1000, 636, (15, 122, 90))
    kicker(d, 544, 424, "THE HAGUE  ·  WORLD COURT", (15, 122, 90))
    y = headline(d, 544, 452, "MYANMAR GUILTY OF GENOCIDE",
                 font(SERIF_BOLD, 33), 436)
    body(d, 544, y + 12,
         "Judges rule 9-6: the 2017 crackdown on the Rohingya was genocide. "
         "Myanmar must pay restitution and investigate.",
         436)
    # (No icon here: the body text fills the panel, and an icon would
    # overlap it. The panel reads cleanly on text alone.)

    # ---- Row 3: Anthropic IPO + Cyclone Akvan ---------------------
    # Anthropic
    panel(d, 24, 652, 500, 856, (91, 74, 138))
    kicker(d, 44, 668, "NASDAQ DEBUT", (91, 74, 138))
    y = headline(d, 44, 696, "ANTHROPIC'S $1.5 TRILLION IPO",
                 font(SERIF_BOLD, 30), 436)
    body(d, 44, y + 12,
         "AI lab prices at $83, opens at $111.50 and closes at $97.17 - "
         "up 17% on its first day.",
         436)
    # small green up arrow in the free top-right corner, beside the kicker
    ax, ay = 466, 682
    d.polygon([(ax, ay - 14), (ax + 12, ay), (ax + 5, ay), (ax + 5, ay + 14),
               (ax - 5, ay + 14), (ax - 5, ay), (ax - 12, ay)],
              fill=(34, 139, 34))

    # Cyclone
    panel(d, 524, 652, 1000, 856, (27, 105, 160))
    kicker(d, 544, 668, "INDIA  ·  BAY OF BENGAL", (27, 105, 160))
    y = headline(d, 544, 696, "CYCLONE AKVAN SLAMS ODISHA",
                 font(SERIF_BOLD, 30), 436)
    body(d, 544, y + 12,
         "300,000 evacuated as the storm makes landfall; 423 rescue teams "
         "deployed and schools shut.",
         436)
    # small cyclone spiral in the free top-right corner, beside the kicker
    cx, cy = 962, 682
    for r in (15, 11, 7):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=200 - r * 8,
              end=380 - r * 8, fill=(27, 105, 160), width=3)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(27, 105, 160))

    # ---- Row 4: Iran + Voyager 1 ----------------------------------
    # One-line headlines (22px) plus one-line subheads (19px): at 24px the
    # headlines wrapped and the second line was clipped by the panel edge.
    panel(d, 24, 872, 500, 960, (120, 100, 40))
    kicker(d, 44, 880, "WASHINGTON", (120, 100, 40))
    fit_headline(d, 44, 906, "IRAN DECISION PUSHED TO 2027", 436)
    body(d, 44, 934, "Trump says no rush; Senate votes 51-48.", 436, size=19)
    panel(d, 524, 872, 1000, 960, (60, 60, 120))
    kicker(d, 544, 880, "SPACE", (60, 60, 120))
    fit_headline(d, 544, 906, "VOYAGER 1: ONE LIGHT-DAY AWAY", 436)
    body(d, 544, 934, "NASA confirms the probe's milestone.", 436, size=19)

    # ---- Footer ticker --------------------------------------------
    d.rectangle([0, 976, W, H], fill=NAVY)
    tick = ("ALSO:  GTA 6 tops $1.80bn  ·  Van Gogh sells for $190.4m  ·  "
            "Gold at a 14-month low  ·  California probes Nvidia")
    # shrink the font until the ticker fits the width with margin
    tsize = 19
    tf2 = font(SANS_BOLD, tsize)
    while d.textlength(tick, font=tf2) > W - 32 and tsize > 12:
        tsize -= 1
        tf2 = font(SANS_BOLD, tsize)
    d.text(((W - d.textlength(tick, font=tf2)) / 2, 994), tick,
           font=tf2, fill=(235, 230, 214))

    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
