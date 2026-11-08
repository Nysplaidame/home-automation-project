from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).with_name("sensor-input-filter-concept.png")
SCALE = 27
ORIGIN = (150, 135)
BOARD = (26.5, 24.0)
COLORS = {
    "ink": "#182231",
    "muted": "#52647b",
    "edge": "#53677d",
    "cut": "#d6e9fa",
    "cut_edge": "#7eb7e6",
    "power": "#d52835",
    "input": "#de7b19",
    "output": "#7849d9",
    "ground": "#222831",
    "pocket": "#7154df",
}

image = Image.new("RGB", (1360, 990), "#f5f7fa")
draw = ImageDraw.Draw(image)
fonts = Path(r"C:\Windows\Fonts")


def font(name, size):
    return ImageFont.truetype(str(fonts / name), size)


title_font = font("segoeuib.ttf", 34)
heading_font = font("segoeuib.ttf", 21)
body_font = font("segoeui.ttf", 17)
small_font = font("segoeui.ttf", 15)
label_font = font("segoeuib.ttf", 16)


def point(x, y):
    return (round(ORIGIN[0] + x * SCALE), round(ORIGIN[1] + y * SCALE))


def path(points, color, width_mm):
    draw.line(
        [point(x, y) for x, y in points],
        fill=color,
        width=max(1, round(width_mm * SCALE)),
        joint="curve",
    )


def label(x, y, value, color, anchor):
    draw.text(point(x, y), value, fill=color, font=label_font, anchor=anchor)


def pocket(x, y, width, height, value):
    left, top = point(x, y)
    right, bottom = point(x + width, y + height)
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=7,
        fill="white",
        outline=COLORS["pocket"],
        width=3,
    )
    draw.text(
        ((left + right) / 2, (top + bottom) / 2),
        value,
        font=label_font,
        fill=COLORS["ink"],
        anchor="mm",
    )


def node(x, y, color):
    px, py = point(x, y)
    draw.ellipse((px - 6, py - 6, px + 6, py + 6), fill=color, outline="white", width=2)


draw.text(
    (60, 31),
    "Sensor input filter  |  provisional carrier concept",
    font=title_font,
    fill=COLORS["ink"],
)
draw.text(
    (61, 77),
    "Illustrative body sizes and 1.2 mm channels; confirm parts, leads and wire before fabrication.",
    font=body_font,
    fill=COLORS["muted"],
)

left, top = point(0, 0)
right, bottom = point(*BOARD)
draw.rounded_rectangle(
    (left, top, right, bottom), radius=14, fill="white", outline=COLORS["edge"], width=3
)

# These channel segments are also the connection table: different nets never
# intersect except through the three component pockets.
segments = [
    ([(0, 2), (18, 2)], "power"),
    ([(18, 2), (18, 3.6)], "power"),
    ([(0, 11.5), (7, 11.5)], "input"),
    ([(13, 11.5), (BOARD[0], 11.5)], "output"),
    ([(18, 9.6), (18, 11.5)], "output"),
    ([(24, 11.5), (24, 14.5)], "output"),
    ([(0, 22), (24, 22)], "ground"),
    ([(24, 19.5), (24, 22)], "ground"),
]
for points, _ in segments:
    path(points, COLORS["cut_edge"], 1.27)
for points, _ in segments:
    path(points, COLORS["cut"], 1.17)
for points, net in segments:
    path(points, COLORS[net], 0.12)

pocket(7, 10.25, 6, 2.5, "1k")
pocket(16.75, 3.6, 2.5, 6, "10k")
pocket(22.75, 14.5, 2.5, 5, "100nF")
for x, y, net in [(18, 2, "power"), (18, 11.5, "output"), (24, 11.5, "output"), (24, 22, "ground")]:
    node(x, y, COLORS[net])

for x, y, value, net, anchor in [
    (-1, 2, "3.3V", "power", "rm"),
    (-1, 11.5, "IN", "input", "rm"),
    (-1, 22, "GND", "ground", "rm"),
    (BOARD[0] + 0.8, 11.5, "OUT", "output", "lm"),
]:
    label(x, y, value, COLORS[net], anchor)

draw.line((left, bottom + 30, right, bottom + 30), fill="#8492a5", width=2)
for x in (left, right):
    draw.line((x, bottom + 22, x, bottom + 38), fill="#8492a5", width=2)
draw.text(((left + right) / 2, bottom + 45), "26.5 mm", font=small_font, fill=COLORS["muted"], anchor="mt")
axis_x = right + 78
draw.line((axis_x, top, axis_x, bottom), fill="#8492a5", width=2)
for y in (top, bottom):
    draw.line((axis_x - 8, y, axis_x + 8, y), fill="#8492a5", width=2)
draw.text((axis_x + 15, (top + bottom) / 2), "24 mm", font=small_font, fill=COLORS["muted"], anchor="lm")

column_x = 1075
draw.text((column_x, 151), "Connections", font=heading_font, fill=COLORS["ink"])
for index, (part, nets) in enumerate(
    [("1k resistor", "IN  ->  OUT"), ("10k resistor", "3.3V  ->  OUT"), ("100nF axial cap", "OUT  ->  GND")]
):
    y = 195 + index * 74
    draw.text((column_x, y), part, font=label_font, fill=COLORS["ink"])
    draw.text((column_x, y + 27), nets, font=body_font, fill=COLORS["muted"])

draw.text((column_x, 480), "Assumed bodies", font=heading_font, fill=COLORS["ink"])
for index, value in enumerate(
    ["1k: 6 x 2.5 mm, axial", "10k: 2.5 x 6 mm, axial", "100nF: 2.5 x 5 mm, axial"]
):
    draw.text((column_x, 520 + index * 34), value, font=body_font, fill=COLORS["muted"])
draw.text((column_x, 681), "Mechanical concept only", font=heading_font, fill=COLORS["ink"])
draw.text((column_x, 719), "No SCAD or STL generated.", font=body_font, fill=COLORS["muted"])

draw.text(
    (60, 908),
    "Plate outline: 26.5 x 24 mm  |  intended height: 3 mm  |  intended recess: 2 mm",
    font=body_font,
    fill=COLORS["muted"],
)
draw.text(
    (60, 936),
    "Fit inputs still needed: actual body thickness, lead diameter, insulation, bend radius and solder access.",
    font=body_font,
    fill=COLORS["muted"],
)

image.save(OUT)
print(OUT)
