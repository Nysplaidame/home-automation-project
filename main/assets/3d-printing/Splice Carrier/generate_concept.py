from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCAD_PATH = Path(__file__).with_name("ventsys_i2c_power_splice.scad")
OUTPUT_PATH = Path(__file__).with_name("ventsys_i2c_power_splice_concept.png")


ASSIGN_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*(.+?)\s*;\s*$")


def parse_scad_variables(path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue
        match = ASSIGN_RE.match(line)
        if not match:
            continue
        name, expr = match.groups()
        if name == "$fn":
            continue
        try:
            value = eval(expr, {"__builtins__": {}}, values)
        except Exception:
            continue
        if isinstance(value, (int, float)):
            values[name] = float(value)
    return values


def load_font(name: str, size: int):
    fallback = "DejaVuSans-Bold.ttf" if "bd" in name else "DejaVuSans.ttf"
    for candidate in (name, fallback):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    v = parse_scad_variables(SCAD_PATH)

    scale = 30
    board_x = 190
    board_y = 160
    img_w, img_h = 1620, 940

    plate_x = v["plate_x"]
    plate_y = v["plate_y"]
    rail_w = v["rail_w"]
    branch_w = v["branch_w"]
    origin_x = v.get("origin_x", 0.0)
    origin_y = v.get("origin_y", 0.0)

    colors = {
        "bg": (246, 248, 252),
        "outline": (43, 49, 63),
        "channel_fill": (214, 221, 231),
        "channel_edge": (108, 122, 145),
        "pocket_fill": (189, 189, 189),
        "pocket_edge": (83, 96, 118),
        "text": (34, 40, 53),
        "sub": (92, 108, 134),
        "red": (240, 68, 60),
        "black": (33, 37, 41),
        "purple": (117, 92, 235),
        "orange": (255, 160, 0),
        "blue": (40, 120, 220),
        "green": (30, 150, 70),
    }

    img = Image.new("RGB", (img_w, img_h), colors["bg"])
    d = ImageDraw.Draw(img)

    font_title = load_font("arialbd.ttf", 30)
    font_body = load_font("arial.ttf", 14)
    font_pocket = load_font("arialbd.ttf", 18)

    def mmx(val: float) -> float:
        return board_x + val * scale

    def mmy(val: float) -> float:
        return board_y + val * scale

    def lx(val: float) -> float:
        return origin_x + val

    def ly(val: float) -> float:
        return origin_y + val

    def rr(box, radius, outline, fill=None, width=1):
        d.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)

    def channel(x: float, y: float, w: float, h: float):
        d.rectangle(
            [mmx(x), mmy(y), mmx(x + w), mmy(y + h)],
            fill=colors["channel_fill"],
            outline=colors["channel_edge"],
            width=1,
        )

    def pocket(x: float, y: float, w: float, h: float, r: float, label: str, sublabel: str | None = None):
        box = [mmx(x), mmy(y), mmx(x + w), mmy(y + h)]
        rr(box, max(3, int(r * scale * 0.3)), colors["pocket_edge"], fill=colors["pocket_fill"], width=2)
        bb = d.textbbox((0, 0), label, font=font_pocket)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = (box[0] + box[2] - tw) / 2
        ty = (box[1] + box[3] - th) / 2 - (10 if sublabel else 0)
        d.text((tx, ty), label, font=font_pocket, fill=colors["text"])
        if sublabel:
            bb2 = d.textbbox((0, 0), sublabel, font=font_body)
            tw2 = bb2[2] - bb2[0]
            d.text(((box[0] + box[2] - tw2) / 2, ty + 28), sublabel, font=font_body, fill=colors["text"])

    def tap(y_pos: float, x0: float, w: float):
        mid = ly(y_pos) + rail_w / 2
        x = lx(x0)
        rr([mmx(x), mmy(mid - w / 2), mmx(plate_x), mmy(mid + w / 2)], 6, colors["channel_edge"], fill=colors["channel_fill"], width=1)

    def line_h(x1: float, x2: float, y: float, color, width: int = 4):
        d.line((mmx(x1), mmy(y), mmx(x2), mmy(y)), fill=color, width=width)

    def line_v(x: float, y1: float, y2: float, color, width: int = 4):
        d.line((mmx(x), mmy(y1), mmx(x), mmy(y2)), fill=color, width=width)

    def node(x: float, y: float, color):
        d.ellipse((mmx(x) - 6, mmy(y) - 6, mmx(x) + 6, mmy(y) + 6), fill=color)

    mids = {n: v[f"rail_{n}_mid"] for n in ("3v3", "gnd", "ldr")}
    col = {"3v3": colors["red"], "gnd": colors["black"], "ldr": colors["green"]}

    d.text((150, 24), "VentSys Sensor Array - Power Splice Carrier  (top-down concept)", font=font_title, fill=colors["text"])
    d.text((40, 100), "ESP32-C6-Zero  -->", font=font_title, fill=colors["text"])
    d.text((mmx(plate_x) - 210, 100), "<--  Sensors", font=font_title, fill=colors["text"])

    rr([mmx(0), mmy(0), mmx(plate_x), mmy(plate_y)], 14, colors["outline"], fill=(250, 250, 252), width=3)

    for n in mids:
        channel(0, ly(v[f"rail_{n}_y"]), plate_x, rail_w)

    rmid = v["r10k_y"] + v["r10k_h"] / 2
    channel(lx(v["r10k_gnd_drop_x"]), ly(v["r10k_gnd_drop_y"]), branch_w, v["r10k_gnd_drop_h"])
    channel(lx(v["r10k_gnd_drop_x"]), ly(rmid - branch_w / 2), v["r10k_gnd_run_w"], branch_w)
    channel(lx(v["r10k_ldr_run_x"]), ly(rmid - branch_w / 2), v["r10k_ldr_run_w"], branch_w)
    rise_x = v["r10k_ldr_run_x"] + v["r10k_ldr_run_w"] - branch_w
    channel(lx(rise_x), ly(v["r10k_ldr_rise_y"]), branch_w, v["r10k_ldr_rise_h"])

    for c in ("cap10", "cap100"):
        channel(lx(v[f"{c}_branch_x"]), ly(v[f"{c}_3v3_branch_y"]), branch_w, v[f"{c}_3v3_branch_h"])
        channel(lx(v[f"{c}_branch_x"]), ly(v[f"{c}_gnd_branch_y"]), branch_w, v[f"{c}_gnd_branch_h"])

    for n, c in col.items():
        line_h(0, plate_x, mids[n], c)

    for c in ("cap10", "cap100"):
        bx = lx(v[f"{c}_branch_x"] + branch_w / 2)
        line_v(bx, ly(v[f"{c}_3v3_branch_y"]), ly(v[f"{c}_3v3_branch_y"] + v[f"{c}_3v3_branch_h"]), colors["red"])
        line_v(bx, ly(v[f"{c}_gnd_branch_y"]), ly(v[f"{c}_gnd_branch_y"] + v[f"{c}_gnd_branch_h"]), colors["black"])
        node(bx, mids["3v3"], colors["red"])
        node(bx, mids["gnd"], colors["black"])

    pocket(lx(v["cap10_x"]), ly(v["cap10_y"]), v["cap10_w"], v["cap10_h"], v["cap10_r"], "10uF", "X7R 16V ceramic")
    pocket(lx(v["cap100_x"]), ly(v["cap100_y"]), v["cap100_w"], v["cap100_h"], v["cap100_r"], "100nF", "ceramic")

    gx = lx(v["r10k_gnd_drop_x"] + branch_w / 2)
    line_v(gx, ly(v["r10k_gnd_drop_y"]), ly(rmid), colors["black"])
    line_h(gx, lx(v["r10k_x"]), ly(rmid), colors["black"])
    node(gx, mids["gnd"], colors["black"])
    rx = lx(rise_x + branch_w / 2)
    line_h(lx(v["r10k_x"] + v["r10k_w"]), rx, ly(rmid), colors["green"])
    line_v(rx, ly(rmid), mids["ldr"], colors["green"])
    node(rx, mids["ldr"], colors["green"])
    pocket(lx(v["r10k_x"]), ly(v["r10k_y"]), v["r10k_w"], v["r10k_h"], v["r10k_r"], "10k")

    taps = {"3v3": "BME / SDP / Smoke / CO / OLED / LDR", "gnd": "BME / SDP / Smoke / CO / OLED", "ldr": "to LDR leg 2"}
    for n, txt in taps.items():
        bb = d.textbbox((0, 0), txt, font=font_body)
        d.text((mmx(plate_x) - (bb[2] - bb[0]) - 8, mmy(mids[n]) - 40), txt, font=font_body, fill=colors["sub"])

    for text, n in [("3V3", "3v3"), ("GND", "gnd"), ("LDR GP0", "ldr")]:
        bb = d.textbbox((0, 0), text, font=font_title)
        d.text((mmx(0) - (bb[2] - bb[0]) - 12, mmy(mids[n]) - 16), text, font=font_title, fill=col[n])
    for text, n in [("3V3 x6", "3v3"), ("GND x5", "gnd"), ("LDR", "ldr")]:
        d.text((mmx(plate_x) + 16, mmy(mids[n]) - 16), text, font=font_title, fill=col[n])

    hx1, hx2, hy = mmx(0), mmx(plate_x), mmy(plate_y) + 30
    vx, vy1, vy2 = mmx(plate_x) + 160, mmy(0), mmy(plate_y)
    d.line((hx1, hy, hx2, hy), fill=colors["outline"], width=2)
    d.line((hx1, hy - 10, hx1, hy + 10), fill=colors["outline"], width=2)
    d.line((hx2, hy - 10, hx2, hy + 10), fill=colors["outline"], width=2)
    d.text(((hx1 + hx2) / 2 - 90, hy + 8), f"W = {plate_x:.2f} mm", font=font_title, fill=colors["text"])
    d.line((vx, vy1, vx, vy2), fill=colors["outline"], width=2)
    d.line((vx - 10, vy1, vx + 10, vy1), fill=colors["outline"], width=2)
    d.line((vx - 10, vy2, vx + 10, vy2), fill=colors["outline"], width=2)
    d.text((vx + 16, (vy1 + vy2) / 2 - 14), f"H = {plate_y:.2f} mm", font=font_title, fill=colors["text"])

    legend_y = mmy(plate_y) + 100
    for i, (label, color) in enumerate([("3V3", colors["red"]), ("GND", colors["black"]), ("LDR", colors["green"])]):
        x = 150 + i * 165
        d.line((x, legend_y, x + 40, legend_y), fill=color, width=6)
        d.text((x + 52, legend_y - 16), label, font=font_title, fill=colors["text"])

    d.text((150, legend_y + 34), "I2C (GP4/GP5) and the smoke (GP3) / CO (GP2) lines bypass this carrier. LDR: 3V3 rail -> LDR -> LDR rail; 10k pulls the rail to GND.", font=font_body, fill=colors["sub"])
    d.text((150, legend_y + 56), "Concept is generated from SCAD variables. Edit the tweak block in the SCAD, then rerun this script.", font=font_body, fill=colors["sub"])

    img.save(OUTPUT_PATH)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
