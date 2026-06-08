from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCAD_PATH = Path(__file__).with_name("servo_wiring_no_led_v16.scad")
OUTPUT_PATH = Path(__file__).with_name("servo_wiring_no_led_v16_concept.png")


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
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    v = parse_scad_variables(SCAD_PATH)

    scale = 44
    board_x = 100
    board_y = 120
    img_w, img_h = 1280, 1260

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

    def line_h(x1: float, x2: float, y: float, color, width: int = 4):
        d.line((mmx(x1), mmy(y), mmx(x2), mmy(y)), fill=color, width=width)

    def line_v(x: float, y1: float, y2: float, color, width: int = 4):
        d.line((mmx(x), mmy(y1), mmx(x), mmy(y2)), fill=color, width=width)

    def node(x: float, y: float, color):
        d.ellipse((mmx(x) - 6, mmy(y) - 6, mmx(x) + 6, mmy(y) + 6), fill=color)

    rail_5v_mid = v["rail_5v_mid"]
    rail_gnd_mid = v["rail_gnd_mid"]
    rail_adc_mid = v["rail_adc_mid"]
    rail_pwm_mid = v["rail_pwm_mid"]

    left_gnd_x = lx(v["left_gnd_drop_x"] + branch_w / 2)
    left_gnd_h_y = ly(v["left_gnd_run_y"] + branch_w / 2)
    shared_fb_x = lx(v["shared_fb_x"] + branch_w / 2)
    right_gnd_x = lx(v["right_gnd_drop_x"] + branch_w / 2)
    right_gnd_h_y = ly(v["right_gnd_run_y"] + branch_w / 2)
    fb_20k_y = ly(v["r20k_fb_run_y"] + branch_w / 2)
    fb_cap_y = ly(v["ceramic_fb_run_y"] + branch_w / 2)

    d.text((100, 24), "ESP32 <-> Servo Feedback Carrier  (top-down concept)", font=font_title, fill=colors["text"])
    d.text((25, 86), "ESP32 D1 Mini  -->", font=font_title, fill=colors["text"])
    d.text((945, 86), "<--  Analog Servo", font=font_title, fill=colors["text"])

    rr([mmx(0), mmy(0), mmx(plate_x), mmy(plate_y)], 18, colors["outline"], fill=(250, 250, 252), width=3)

    for y in (v["rail_5v_y"], v["rail_gnd_y"], v["rail_adc_y"], v["rail_pwm_y"]):
        channel(0, ly(y), plate_x, rail_w)

    channel(lx(v["left_gnd_drop_x"]), ly(v["left_gnd_drop_y"]), branch_w, v["left_gnd_drop_h"])
    channel(lx(v["left_gnd_run_x"]), ly(v["left_gnd_run_y"]), v["left_gnd_run_w"], branch_w)
    channel(lx(v["shared_fb_x"]), ly(v["shared_fb_y"]), branch_w, v["shared_fb_h"] + v["join_overlap"])
    channel(lx(v["r20k_fb_run_x"]), ly(v["r20k_fb_run_y"]), v["r20k_fb_run_w"] + v["join_overlap"], branch_w)
    channel(lx(v["ceramic_fb_run_x"]), ly(v["ceramic_fb_run_y"]), v["ceramic_fb_run_w"] + v["join_overlap"], branch_w)
    channel(lx(v["right_gnd_drop_x"]), ly(v["right_gnd_drop_y"]), branch_w, v["right_gnd_drop_h"] + v["join_overlap"])
    channel(lx(v["right_gnd_run_x"]), ly(v["right_gnd_run_y"]), v["right_gnd_run_w"] + v["join_overlap"], branch_w)
    channel(lx(v["elcap_branch_x"]), ly(v["elcap_5v_branch_y"]), branch_w, v["elcap_5v_branch_h"])
    channel(lx(v["elcap_branch_x"]), ly(v["elcap_gnd_branch_y"]), branch_w, v["elcap_gnd_branch_h"])

    line_h(0, plate_x, rail_5v_mid, colors["red"])
    line_h(0, plate_x, rail_gnd_mid, colors["black"])
    line_h(0, plate_x, rail_adc_mid, colors["purple"])
    line_h(0, plate_x, rail_pwm_mid, colors["orange"])
    line_v(lx(v["elcap_branch_x"] + branch_w / 2), ly(v["elcap_5v_branch_y"]), ly(v["elcap_5v_branch_y"] + v["elcap_5v_branch_h"]), colors["red"])
    line_v(lx(v["elcap_branch_x"] + branch_w / 2), ly(v["elcap_gnd_branch_y"]), ly(v["elcap_gnd_branch_y"] + v["elcap_gnd_branch_h"]), colors["black"])
    line_v(left_gnd_x, ly(v["left_gnd_drop_y"]), ly(v["left_gnd_drop_y"] + v["left_gnd_drop_h"]), colors["black"])
    line_h(left_gnd_x, lx(v["left_gnd_run_x"] + v["left_gnd_run_w"]), left_gnd_h_y, colors["black"])
    line_h(lx(v["r20k_fb_run_x"]), lx(v["r20k_fb_run_x"] + v["r20k_fb_run_w"]), fb_20k_y, colors["purple"])
    line_v(shared_fb_x, ly(v["shared_fb_y"]), ly(v["shared_fb_y"] + v["shared_fb_h"]), colors["purple"])
    line_h(shared_fb_x, lx(v["ceramic_fb_run_x"] + v["ceramic_fb_run_w"]), fb_cap_y, colors["purple"])
    line_v(right_gnd_x, ly(v["right_gnd_drop_y"]), ly(v["right_gnd_drop_y"] + v["right_gnd_drop_h"]), colors["black"])
    line_h(lx(v["right_gnd_run_x"]), lx(v["right_gnd_run_x"] + v["right_gnd_run_w"]), right_gnd_h_y, colors["black"])

    pocket(lx(v["elcap_x"]), ly(v["elcap_y"]), v["elcap_w"], v["elcap_h"], v["elcap_r"], "470-1000uF", "electrolytic")
    pocket(lx(v["r20k_x"]), ly(v["r20k_y"]), v["r20k_w"], v["r20k_h"], v["r20k_r"], "20k")
    pocket(lx(v["ceramic_x"]), ly(v["ceramic_y"]), v["ceramic_w"], v["ceramic_h"], v["ceramic_r"], "100nF")
    pocket(lx(v["r10k_x"]), ly(v["r10k_y"]), v["r10k_w"], v["r10k_h"], v["r10k_r"], "10k")

    for x, y, c in [
        (lx(v["elcap_branch_x"] + branch_w / 2), rail_5v_mid, colors["red"]),
        (lx(v["elcap_branch_x"] + branch_w / 2), rail_gnd_mid, colors["black"]),
        (left_gnd_x, rail_gnd_mid, colors["black"]),
        (shared_fb_x, rail_adc_mid, colors["purple"]),
        (right_gnd_x, rail_gnd_mid, colors["black"]),
    ]:
        node(x, y, c)

    for text, x, y, color in [
        ("5V", mmx(0) - 42, mmy(rail_5v_mid) - 12, colors["red"]),
        ("GND", mmx(0) - 60, mmy(rail_gnd_mid) - 12, colors["black"]),
        ("ADC", mmx(0) - 58, mmy(rail_adc_mid) - 12, colors["purple"]),
        ("PWM", mmx(0) - 50, mmy(rail_pwm_mid) - 12, colors["orange"]),
        ("5V", mmx(plate_x) + 18, mmy(rail_5v_mid) - 12, colors["red"]),
        ("GND", mmx(plate_x) + 18, mmy(rail_gnd_mid) - 12, colors["black"]),
        ("FB", mmx(plate_x) + 18, mmy(rail_adc_mid) - 12, colors["purple"]),
        ("PWM", mmx(plate_x) + 18, mmy(rail_pwm_mid) - 12, colors["orange"]),
    ]:
        d.text((x, y), text, font=font_title, fill=color)

    hx1, hx2, hy = mmx(0), mmx(plate_x), mmy(plate_y) + 34
    vx, vy1, vy2 = mmx(plate_x) + 140, mmy(0), mmy(plate_y)
    d.line((hx1, hy, hx2, hy), fill=colors["outline"], width=2)
    d.line((hx1, hy - 10, hx1, hy + 10), fill=colors["outline"], width=2)
    d.line((hx2, hy - 10, hx2, hy + 10), fill=colors["outline"], width=2)
    d.text(((hx1 + hx2) / 2 - 65, hy + 10), f"W = {plate_x:.2f} mm", font=font_title, fill=colors["text"])
    d.line((vx, vy1, vx, vy2), fill=colors["outline"], width=2)
    d.line((vx - 10, vy1, vx + 10, vy1), fill=colors["outline"], width=2)
    d.line((vx - 10, vy2, vx + 10, vy2), fill=colors["outline"], width=2)
    d.text((vx + 16, (vy1 + vy2) / 2 - 14), f"H = {plate_y:.2f} mm", font=font_title, fill=colors["text"])

    legend_y = mmy(plate_y) + 78
    for i, (label, color) in enumerate([
        ("5V", colors["red"]),
        ("GND", colors["black"]),
        ("PWM", colors["orange"]),
        ("feedback / ADC", colors["purple"]),
    ]):
        x = 100 + i * 120
        d.line((x, legend_y, x + 40, legend_y), fill=color, width=6)
        d.text((x + 52, legend_y - 12), label, font=font_title, fill=colors["text"])

    d.text((100, legend_y + 38), "Concept is generated from SCAD variables. Edit the tweak block in the SCAD, then rerun this script.", font=font_body, fill=colors["sub"])

    img.save(OUTPUT_PATH)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
