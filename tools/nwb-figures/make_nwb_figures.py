"""Generate the NWB file-organization figures for the gui-docs NWB format page.

The figures mimic the style of the existing gui-docs figures (format-illustrations.ai): the icons
(icons/) are cropped from the previous NWB figures, the text uses Source Sans Pro SemiBold, and the tree
lines, font size and spacing are measured from the previous figures. Requires ImageMagick 7 (magick).

Usage: python3 make_nwb_figures.py <SourceSansPro-Semibold.otf> [<out_dir>]
(<out_dir> defaults to source/_static/images/recordingdata/nwb)
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICON_DIR = HERE / "icons"
DEFAULT_OUT_DIR = HERE.parents[1] / "source" / "_static" / "images" / "recordingdata" / "nwb"

# Geometry measured from the original figures (pixels)
ROW_PITCH = 98  # vertical distance of the rows
LINE_WIDTH = 7.5  # width of the tree lines
FONT_SIZE = 44  # cap height of 29 px
TEXT_GAP = 24  # gap between icon and text
BASELINE = 15  # text baseline below the row center
CHILD_OFFSET = 46  # left edge of a child icon right of the parent's vertical line
LINE_GAP_TOP = 9  # gap between the parent icon and its vertical line
LINE_GAP_RIGHT = 14  # gap between a horizontal line and the child icon
MARGIN = 12

ICONS = {"folder": (76, 68), "file": (64, 75), "group": (64, 64), "dataset": (66, 77)}


def layout(tree, depth=0, x=MARGIN, rows=None):
    """Assign a row and position to each node; tree = (icon, label, [children])."""
    rows = [] if rows is None else rows
    icon, label, children = tree
    width, height = ICONS[icon]
    node = {"icon": icon, "label": label, "row": len(rows), "x": x, "w": width, "h": height, "children": []}
    rows.append(node)
    center_x = x + width / 2
    for child in children:
        node["children"].append(layout(child, depth + 1, center_x + CHILD_OFFSET, rows))
    return node


def draw_commands(node, icon_dir):
    cmds = []
    cy = MARGIN + 40 + node["row"] * ROW_PITCH
    top = cy - node["h"] / 2
    cmds += ["-draw", f"image over {node['x']},{top:.1f} {node['w']},{node['h']} '{icon_dir}/icon_{node['icon']}.png'"]
    cmds += ["-draw", f"text {node['x'] + node['w'] + TEXT_GAP},{cy + BASELINE} '{node['label']}'"]
    if node["children"]:
        lx = node["x"] + node["w"] / 2
        last_cy = MARGIN + 40 + node["children"][-1]["row"] * ROW_PITCH
        half = LINE_WIDTH / 2
        cmds += ["-draw", f"rectangle {lx - half:.2f},{cy + node['h'] / 2 + LINE_GAP_TOP:.2f} {lx + half:.2f},{last_cy + half:.2f}"]
        for child in node["children"]:
            ccy = MARGIN + 40 + child["row"] * ROW_PITCH
            cmds += ["-draw", f"rectangle {lx - half:.2f},{ccy - half:.2f} {child['x'] - LINE_GAP_RIGHT:.2f},{ccy + half:.2f}"]
            cmds += draw_commands(child, icon_dir)
    return cmds


def render(tree, icon_dir, font, out):
    root = layout(tree)
    num_rows = 1 + count(root)
    height = 2 * MARGIN + 80 + (num_rows - 1) * ROW_PITCH
    cmd = ["magick", "-size", f"3000x{height}", "xc:white", "-fill", "black", "-stroke", "none",
           "-font", font, "-pointsize", str(FONT_SIZE)]
    cmd += draw_commands(root, icon_dir)
    # crop to the content and add a white margin, as in the original figures
    cmd += ["-trim", "+repage", "-bordercolor", "white", "-border", f"{MARGIN}", "-strip", "-depth", "8", out]
    subprocess.run(cmd, check=True)


def count(node):
    return sum(1 + count(c) for c in node["children"])


def group(label, *children):
    return ("group", label, list(children))


def dataset(label):
    return ("dataset", label, [])


FIGURES = {
    "organization": ("folder", "Record Node 101", [
        ("file", "experiment1.nwb", [
            group("acquisition", group("processor1.stream1"), group("processor2.stream1.electrode1")),
            group("events", group("processor1.stream1.TTL"), group("messages"), group("sync_messages")),
            group("intervals", group("epochs")),
            group("general", group("extracellular_ephys", group("electrodes")), group("subject")),
        ]),
    ]),
    "continuous": group("processor1.stream1", dataset("data"), dataset("timestamps"), dataset("channel_conversion"),
                        dataset("electrodes"), group("sync", dataset("sample_numbers"))),
    "events": group("processor1.stream1.TTL", dataset("timestamp"), dataset("line"), dataset("state"),
                    dataset("full_word"), dataset("sample_number")),
    "spikes": group("processor2.stream1.electrode1", dataset("data"), dataset("timestamps"), dataset("electrodes"),
                    group("sync", dataset("sample_numbers"))),
}

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    font = sys.argv[1]
    out_dir = Path(sys.argv[2]) if len(sys.argv) == 3 else DEFAULT_OUT_DIR
    for name, tree in FIGURES.items():
        out = out_dir / f"{name}.png"
        render(tree, ICON_DIR, font, str(out))
        print(out)
