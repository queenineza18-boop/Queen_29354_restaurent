#!/usr/bin/env python3
"""Draw the ROSTS logical ERD (crow's foot) as docs/design/erd.png.

Phase II, INSY 8311. The drawing is generated rather than hand-placed so the
boxes, the cardinality marks and the routing stay consistent if an entity is
edited. Run from the repository root:

    python tools/make_erd.py            # writes docs/design/erd.png
    python tools/make_erd.py --check    # also report any connector that
                                       # crosses a box it does not belong to

Requires matplotlib (pip install matplotlib).
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# --------------------------------------------------------------------------
# Canvas and palette
# --------------------------------------------------------------------------
W, H = 192.0, 116.0          # drawing units; 1 unit ~ 15 px at dpi 150
ROW_H = 1.55                 # height of one attribute row
TITLE_H = 2.6                # height of the entity title bar
BOX_W = 28.0

INK = "#1b2431"
MUTED = "#5c6b7f"
RULE = "#b8c2cf"
HEAD = "#1f3a5f"
FILL = "#ffffff"
KEY = "#0f766e"              # primary key
FKCOL = "#a16207"            # foreign key
BG = "#f7f9fb"

# --------------------------------------------------------------------------
# Entities: id -> (column-x, top-y, [rows])
# A row is (kind, text): kind is "pk", "fk", "pkfk", "u" or "" (plain).
# --------------------------------------------------------------------------
ENTITIES = {
    "OUTLET": (2, 100, [
        ("pk", "outlet_code"), ("", "outlet_name"), ("", "city"),
        ("", "opening_date"), ("", "is_active"),
    ]),
    "STAFF": (40, 100, [
        ("pk", "staff_id"), ("fk", "outlet_code"), ("", "full_name"),
        ("", "role"), ("", "hire_date"), ("", "is_active"),
    ]),
    "ORDERS": (78, 100, [
        ("pk", "order_id"), ("u", "order_no"), ("fk", "outlet_code"),
        ("fk", "staff_id"), ("", "ordered_at"), ("", "status"),
        ("", "net_amount"), ("", "tax_amount"), ("", "total_amount"),
        ("", "amount_paid"),
    ]),
    "PAYMENT": (118, 100, [
        ("pk", "payment_id"), ("fk", "order_id"), ("fk", "method_code"),
        ("", "paid_at"), ("", "amount"), ("", "status"),
    ]),
    "PAYMENT_METHOD": (156, 100, [
        ("pk", "method_code"), ("", "method_name"), ("", "is_cash"),
    ]),
    "MENU_CATEGORY": (2, 66, [
        ("pk", "category_id"), ("", "category_name"),
    ]),
    "MENU_ITEM": (40, 66, [
        ("pk", "menu_item_id"), ("fk", "category_id"), ("", "item_name"),
        ("", "variant"), ("", "unit_price"), ("", "description"),
        ("", "is_active"),
    ]),
    "ORDER_LINE": (78, 66, [
        ("pk", "order_line_id"), ("fk", "order_id"), ("fk", "menu_item_id"),
        ("u", "line_no"), ("", "quantity"), ("", "unit_price"),
        ("", "line_total"),
    ]),
    "ORDER_PROMOTION": (118, 66, [
        ("pk", "order_promotion_id"), ("fk", "order_id"),
        ("fk", "promotion_id"), ("", "discount_pct"), ("", "discount_amount"),
    ]),
    "PROMOTION": (156, 66, [
        ("pk", "promotion_id"), ("", "promo_name"), ("", "discount_pct"),
        ("", "valid_from"), ("", "valid_to"),
    ]),
    "INGREDIENT": (2, 32, [
        ("pk", "ingredient_id"), ("", "ingredient_name"), ("", "unit"),
        ("", "qty_on_hand"), ("", "reorder_level"),
    ]),
    "MENU_ITEM_INGREDIENT": (40, 32, [
        ("pkfk", "menu_item_id"), ("pkfk", "ingredient_id"),
        ("", "qty_per_unit"),
    ]),
    "STOCK_MOVEMENT": (78, 32, [
        ("pk", "movement_id"), ("fk", "ingredient_id"), ("fk", "order_id"),
        ("", "movement_type"), ("", "qty"), ("", "moved_at"),
    ]),
    "PRICE_HISTORY": (118, 32, [
        ("pk", "price_history_id"), ("fk", "menu_item_id"),
        ("", "old_price"), ("", "new_price"), ("", "changed_by"),
        ("", "changed_at"),
    ]),
    "AUDIT_LOG": (156, 32, [
        ("pk", "audit_id"), ("", "table_name"), ("", "record_key"),
        ("", "action"), ("", "old_value"), ("", "new_value"),
        ("", "db_user"), ("", "logged_at"),
    ]),
}

BOTTOM = 15.0  # lowest y used, for the caption


def box_geometry(rows):
    h = TITLE_H + ROW_H * len(rows) + 0.9
    return h


def rect_of(name):
    x, top, rows = ENTITIES[name]
    return (x, top - box_geometry(rows), x + BOX_W, top)  # x0, y0, x1, y1


def draw_entity(ax, name):
    x, top, rows = ENTITIES[name]
    h = box_geometry(rows)
    y0 = top - h

    ax.add_patch(FancyBboxPatch(
        (x, y0), BOX_W, h,
        boxstyle="round,pad=0.0,rounding_size=0.8",
        linewidth=1.0, edgecolor=RULE, facecolor=FILL, zorder=3,
    ))
    ax.add_patch(FancyBboxPatch(
        (x, top - TITLE_H), BOX_W, TITLE_H,
        boxstyle="round,pad=0.0,rounding_size=0.8",
        linewidth=0, facecolor=HEAD, zorder=4,
    ))
    # square off the bottom of the title bar so it meets the body cleanly
    ax.add_patch(Rectangle((x, top - TITLE_H), BOX_W, 0.7,
                           linewidth=0, facecolor=HEAD, zorder=4))
    ax.text(x + BOX_W / 2, top - TITLE_H / 2 - 0.15, name,
            ha="center", va="center", fontsize=8.2, fontweight="bold",
            color="#ffffff", zorder=5, family="DejaVu Sans")

    for i, (kind, text) in enumerate(rows):
        y = top - TITLE_H - ROW_H * (i + 0.5) - 0.35
        if i % 2:
            ax.add_patch(Rectangle((x + 0.35, y - ROW_H / 2), BOX_W - 0.7,
                                   ROW_H, linewidth=0, facecolor="#f3f6f9",
                                   zorder=3))
        if kind == "pk":
            ax.text(x + 1.4, y, "PK", fontsize=5.4, va="center", ha="left",
                    color=KEY, fontweight="bold", zorder=5)
            ax.text(x + 5.4, y, text, fontsize=6.6, va="center", ha="left",
                    color=INK, fontweight="bold", zorder=5)
        elif kind == "fk":
            ax.text(x + 1.4, y, "FK", fontsize=5.4, va="center", ha="left",
                    color=FKCOL, fontweight="bold", zorder=5)
            ax.text(x + 5.4, y, text, fontsize=6.6, va="center", ha="left",
                    color=INK, zorder=5)
        elif kind == "pkfk":
            ax.text(x + 1.4, y, "PKFK", fontsize=5.0, va="center", ha="left",
                    color=KEY, fontweight="bold", zorder=5)
            ax.text(x + 6.0, y, text, fontsize=6.6, va="center", ha="left",
                    color=INK, fontweight="bold", zorder=5)
        elif kind == "u":
            ax.text(x + 1.4, y, "U", fontsize=5.4, va="center", ha="left",
                    color=MUTED, fontweight="bold", zorder=5)
            ax.text(x + 5.4, y, text, fontsize=6.6, va="center", ha="left",
                    color=INK, zorder=5)
        else:
            ax.text(x + 2.6, y, text, fontsize=6.6, va="center", ha="left",
                    color=INK, zorder=5)


# --------------------------------------------------------------------------
# Relationship drawing
# --------------------------------------------------------------------------
def _norm(dx, dy):
    m = (dx * dx + dy * dy) ** 0.5 or 1.0
    return dx / m, dy / m


def draw_one(ax, point, outward):
    """A tick across the connector, at the 'one' end."""
    px, py = point
    ox, oy = _norm(*outward)
    nx, ny = -oy, ox
    ax.plot([px + nx * 1.6, px - nx * 1.6], [py + ny * 1.6, py - ny * 1.6],
            color=INK, linewidth=1.1, zorder=6, solid_capstyle="round")


def draw_many(ax, point, outward):
    """Three prongs opening away from the box: the crow's foot."""
    px, py = point
    dx, dy = _norm(*outward)            # pointing away from the box
    nx, ny = -dy, dx
    for spread in (-2.0, 0.0, 2.0):
        ax.plot([px, px + dx * 4.4 + nx * spread],
                [py, py + dy * 4.4 + ny * spread],
                color=INK, linewidth=0.95, zorder=6, solid_capstyle="round")


def draw_link(ax, points, one_at_start):
    """Draw an orthogonal connector given waypoints."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.plot(xs, ys, color=INK, linewidth=1.0, zorder=6,
            solid_capstyle="butt", solid_joinstyle="miter")

    # outward = away from the box, along the connector
    start_out = (points[1][0] - points[0][0], points[1][1] - points[0][1])
    end_out = (points[-2][0] - points[-1][0], points[-2][1] - points[-1][1])

    if one_at_start:
        draw_one(ax, points[0], start_out)
        draw_many(ax, points[-1], end_out)
    else:
        draw_many(ax, points[0], start_out)
        draw_one(ax, points[-1], end_out)


LINKS = [
    # name, waypoints, one end is at the start of the list
    ("outlet_staff", [(30, 97), (40, 97)], True),
    ("staff_orders", [(68, 97), (78, 97)], True),
    ("outlet_orders", [(12, 100), (12, 107), (92, 107), (92, 100)], True),
    ("category_item", [(30, 62), (40, 62)], True),
    ("item_line", [(68, 62), (78, 62)], True),
    ("orders_line", [(92, 81.1), (92, 66)], True),
    ("orders_payment", [(106, 97), (118, 97)], True),
    ("payment_method", [(146, 97), (156, 97)], True),
    ("orders_ordpromo", [(106, 91), (111.5, 91), (111.5, 62), (118, 62)], True),
    ("promo_ordpromo", [(156, 62), (146, 62)], True),
    ("item_recipe", [(48, 51.65), (48, 32)], True),
    ("ingredient_recipe", [(30, 29), (40, 29)], True),
    ("ingredient_stock", [(12, 20.75), (12, 13.5), (86, 13.5), (86, 19.2)],
     True),
    ("orders_stock", [(106, 84.5), (108.5, 84.5), (108.5, 26), (106, 26)],
     True),
    ("item_price", [(60, 51.65), (60, 48), (114.5, 48), (114.5, 26),
                    (118, 26)], True),
]


def segments_cross_box(points, boxes):
    """Return boxes whose interior a connector segment passes through."""
    hits = []
    for name, (x0, y0, x1, y1) in boxes.items():
        for (ax_, ay), (bx, by) in zip(points, points[1:]):
            steps = max(2, int(max(abs(bx - ax_), abs(by - ay)) * 6))
            for s in range(1, steps):
                t = s / steps
                x, y = ax_ + (bx - ax_) * t, ay + (by - ay) * t
                if x0 + 0.4 < x < x1 - 0.4 and y0 + 0.4 < y < y1 - 0.4:
                    if name not in hits:
                        hits.append(name)
                    break
    return hits


def build(check=False):
    fig, ax = plt.subplots(figsize=(19.2, 11.6), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, W)
    ax.set_ylim(9, H)
    ax.axis("off")

    boxes = {n: rect_of(n) for n in ENTITIES}
    problems = []
    if check:
        for name, pts, _ in LINKS:
            hits = segments_cross_box(pts, boxes)
            if hits:
                problems.append((name, hits))

    # title
    ax.text(2, 113.4, "ROSTS · Logical ERD in third normal form",
            fontsize=13.5, fontweight="bold", color=INK, ha="left", va="center")
    ax.text(2, 111.0,
            "Restaurant Order and Sales Tracking System · Queen Ineza · 29354 · "
            "INSY 8311 Phase II · 15 entities, crow's-foot notation",
            fontsize=7.6, color=MUTED, ha="left", va="center")
    ax.plot([2, W - 8], [109.2, 109.2], color=RULE, linewidth=0.9)

    for name in ENTITIES:
        draw_entity(ax, name)
    for _name, pts, one_start in LINKS:
        draw_link(ax, pts, one_start)

    # note on the audit log
    ax.text(156 + BOX_W / 2, 14.2,
            "no foreign key: AUDIT_LOG points at any table\n"
            "by its name and record key",
            fontsize=6.2, color=MUTED, ha="center", va="top", style="italic")

    # legend, in the empty block under MENU_CATEGORY
    lx, ly, lw, lh = 2, 38.0, 36, 18.0
    ax.add_patch(FancyBboxPatch((lx, ly), lw, lh,
                                boxstyle="round,pad=0.0,rounding_size=0.6",
                                linewidth=0.9, edgecolor=RULE, facecolor=FILL,
                                zorder=3))
    ax.text(lx + 1.8, ly + lh - 1.7, "Legend", fontsize=7.0,
            fontweight="bold", color=INK, va="center", zorder=5)

    rows = [
        ("PK", KEY, "primary key"),
        ("FK", FKCOL, "foreign key"),
        ("U", MUTED, "alternate key"),
        ("PKFK", KEY, "part of a composite key"),
    ]
    for i, (tag, colour, meaning) in enumerate(rows):
        py = ly + lh - 3.6 - i * 2.0
        ax.text(lx + 1.8, py, tag, fontsize=5.6, color=colour,
                fontweight="bold", va="center", zorder=5)
        ax.text(lx + 8.4, py, meaning, fontsize=6.0, color=INK,
                va="center", zorder=5)

    # sample cardinality marks, each on its own line
    py = ly + 4.2
    ax.plot([lx + 1.8, lx + 9.5], [py, py], color=INK, linewidth=1.0,
            zorder=5)
    draw_one(ax, (lx + 9.5, py), (1, 0))
    ax.text(lx + 16.5, py, "exactly one", fontsize=6.0, color=MUTED,
            va="center", zorder=5)
    py = ly + 2.0
    ax.plot([lx + 1.8, lx + 9.5], [py, py], color=INK, linewidth=1.0,
            zorder=5)
    draw_many(ax, (lx + 9.5, py), (1, 0))
    ax.text(lx + 16.5, py, "one or many", fontsize=6.0, color=MUTED,
            va="center", zorder=5)

    out = "docs/design/erd.png"
    fig.savefig(out, dpi=100, bbox_inches="tight", facecolor=BG,
                pad_inches=0.25)
    plt.close(fig)

    # The committed PNG is a flat-colour diagram, so a small palette keeps it
    # sharp while making the file about a quarter of its RGBA size. Optional:
    # without Pillow the image is still written, just larger.
    try:
        from PIL import Image

        im = Image.open(out).convert("RGB")
        # a fixed 14-colour palette: the diagram only uses these, and pinning
        # them keeps the PK/FK accents exact instead of merging them into grey
        hexes = ["#f7f9fb", "#ffffff", "#f3f6f9", "#dfe6ee", "#b8c2cf",
                 "#a8b3bf", "#8d99a8", "#5c6b7f", "#3d4d5f", "#1b2431",
                 "#1f3a5f", "#0f766e", "#a16207", "#6f8f8a"]
        flat = []
        for h in hexes:
            flat += [int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)]
        palette = Image.new("P", (1, 1))
        palette.putpalette(flat + [0] * (768 - len(flat)))
        im.quantize(palette=palette, dither=Image.NONE).save(out,
                                                             optimize=True)
    except ImportError:
        pass

    print(f"wrote {out}")

    if check:
        if problems:
            for name, hits in problems:
                print(f"CROSSING: {name} passes through {', '.join(hits)}")
            return 1
        print("no connector crosses a box")
    return 0


if __name__ == "__main__":
    sys.exit(build(check="--check" in sys.argv))
