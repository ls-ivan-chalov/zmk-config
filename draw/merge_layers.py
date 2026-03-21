#!/usr/bin/env python3
"""
Merge keymap-drawer's per-layer YAML into a single overview YAML
where all layers are shown on one keyboard with color-coded legends.

Legend position mapping:
  - tap (center):      Base layer tap action
  - hold (bottom):     Base layer hold action
  - shifted (top):     Base layer shifted action (morphs like , -> ;)
  - tl (top-left):     Fn layer
  - tr (top-right):    Nav layer
  - bl (bottom-left):  Num layer

Colors are applied via CSS classes on legend positions in svg_extra_style.
Combos are drawn as separate mini-diagrams below the main keyboard.
"""

import re
import sys
import yaml


def normalize_key(key):
    """Normalize a key entry into a dict with at least a 't' field."""
    if isinstance(key, str):
        return {"t": key} if key else {}
    if isinstance(key, dict):
        return dict(key)
    return {}


def is_trans(key):
    """Check if a key is transparent."""
    k = normalize_key(key)
    return k.get("type") == "trans"


def is_held(key):
    """Check if a key is a held marker."""
    k = normalize_key(key)
    return k.get("type") == "held"


def get_tap(key):
    """Get tap legend from a key, return empty string for trans/held/empty."""
    k = normalize_key(key)
    if k.get("type") in ("trans", "held"):
        return ""
    return k.get("t", "")


def get_hold(key):
    """Get hold legend from a key."""
    k = normalize_key(key)
    return k.get("h", "")


def get_shifted(key):
    """Get shifted legend from a key."""
    k = normalize_key(key)
    return k.get("s", "")


def shorten_legend(text):
    """Shorten long legends to fit corner positions."""
    short = {
        "Prev App": "PApp",
        "Next App": "NApp",
        "Prev Desk": "PDsk",
        "Next Desk": "NDsk",
        "Spotlight": "Sptlt",
        "Mission Ctrl": "MC",
        "Smart Mouse": "Mouse",
        "Shift+Leader": "S+Ldr",
        "Sticky Num": "S.Num",
        "CANCEL": "Cancl",
        "Left Click": "LClk",
        "Middle Click": "MClk",
        "Right Click": "RClk",
        "Ctl+Bspc": "C+Bs",
        "Ctl+Home": "C+Hm",
        "Ctl+End": "C+End",
        "Ctl+Del": "C+Del",
        "Sentence": "Sent.",
        "Numword": "Numwd",
    }
    return short.get(text, text)


def merge_layers(input_path, output_path):
    with open(input_path) as f:
        data = yaml.safe_load(f)

    layers = data.get("layers", {})
    combos = data.get("combos", [])

    base_keys = layers.get("Base", [])
    nav_keys = layers.get("Nav", [])
    fn_keys = layers.get("Fn", [])
    num_keys = layers.get("Num", [])

    num_keys_count = len(base_keys)

    # Leader key sequence legends (position index -> character).
    # German umlauts via Leader + key (macOS dead-key compose).
    # 40-key five_col_transform positions (display slots at 5,6,17,18):
    #   0:Q  1:W  2:F  3:P  4:B  [5:d 6:d]  7:J  8:L  9:U 10:Y 11:'
    #  12:A 13:R 14:S 15:T 16:G [17:d 18:d] 19:M 20:N 21:E 22:I 23:O
    #  24:Z 25:X 26:C 27:D 28:V  29:K 30:H 31:,  32:. 33:?
    leader_legends = {
        12: "ä",  # Leader + A
        23: "ö",  # Leader + O
         9: "ü",  # Leader + U
        14: "ß",  # Leader + S
    }
    merged = []

    for i in range(num_keys_count):
        base = normalize_key(base_keys[i]) if i < len(base_keys) else {}
        nav = normalize_key(nav_keys[i]) if i < len(nav_keys) else {}
        fn = normalize_key(fn_keys[i]) if i < len(fn_keys) else {}
        num = normalize_key(num_keys[i]) if i < len(num_keys) else {}

        out = {}

        # Center: base tap
        tap = base.get("t", "")
        if tap:
            out["t"] = tap

        # Bottom: base hold
        hold = base.get("h", "")
        if hold:
            out["h"] = hold

        # Top: base shifted
        shifted = base.get("s", "")
        if shifted:
            out["s"] = shorten_legend(shifted)

        # Thumb keys are smaller and rotated — limit overlay legends to avoid
        # clutter. Match Urob's overview style:
        #   Spc/Nav, Enter/Fn: tap + hold only (held on Nav/Fn, skip overlays)
        #   Numword/Num: tap + hold + Fn/Nav overlays (mute icon + Cancel)
        #   Magic/Shift: tap + hold only (skip overlays — too cramped)
        # For thumbs, skip shifted (s) and Num overlay — too cramped.
        is_thumb = i >= num_keys_count - 4
        is_outer_thumb = (i == num_keys_count - 1) or (i == num_keys_count - 4)

        if is_thumb:
            # Drop shifted legend on thumbs — too cramped
            out.pop("s", None)

        # Nav layer (skip trans/held)
        nav_tap = get_tap(nav_keys[i]) if i < len(nav_keys) else ""
        if nav_tap and not is_trans(nav_keys[i]) and not is_held(nav_keys[i]):
            if not is_outer_thumb:
                out["tr"] = shorten_legend(nav_tap)

        # Fn layer (skip trans/held)
        fn_tap = get_tap(fn_keys[i]) if i < len(fn_keys) else ""
        if fn_tap and not is_trans(fn_keys[i]) and not is_held(fn_keys[i]):
            if not is_outer_thumb:
                out["tl"] = shorten_legend(fn_tap)

        # Num layer (skip trans/held; skip on thumbs — too cramped)
        num_tap = get_tap(num_keys[i]) if i < len(num_keys) else ""
        if num_tap and not is_trans(num_keys[i]) and not is_held(num_keys[i]):
            if not is_thumb:
                out["bl"] = shorten_legend(num_tap)

        # Leader sequence legends (bottom-right)
        if i in leader_legends:
            out["br"] = leader_legends[i]

        # If key is completely empty, just output empty string
        if not out:
            merged.append("")
        elif list(out.keys()) == ["t"]:
            # Simple key with just tap
            merged.append(out["t"])
        else:
            merged.append(out)

    # Build combos on a single "Combos" layer below the overview
    merged_combos = []
    for combo in combos:
        c = dict(combo)
        if c.get("hidden"):
            continue
        c["l"] = ["Combos"]
        merged_combos.append(c)

    # Create empty key lists for the combo layer (34 ghost keys)
    ghost_layer = [{"type": "ghost"}] * num_keys_count

    # Build output YAML
    output = {
        "layout": {"qmk_keyboard": "ferris/sweep"},
        "layers": {
            "Overview": merged,
            "Combos": ghost_layer,
        },
        "combos": merged_combos,
        "draw_config": {
            "key_w": 76,
            "key_h": 72,
            "split_gap": 40,
            "combo_w": 36,
            "combo_h": 30,
            "inner_pad_w": 3,
            "inner_pad_h": 3,
            "small_pad": 2,
            "shrink_wide_legends": 5,
            "n_columns": 1,
            "append_colon_to_layer_header": False,
            "dark_mode": "auto",
            "footer_text": '<tspan style="fill: #24292e; font-weight: bold">Base</tspan>  <tspan style="fill: #e05050">Fn</tspan>  <tspan style="fill: #2979ff">Nav</tspan>  <tspan style="fill: #2e9e5e">Num</tspan>  <tspan style="fill: #9c5ec0">Shifted</tspan>  <tspan style="fill: #808890">Hold</tspan>  <tspan style="fill: #e67e22">Leader</tspan>',
            "separate_combo_diagrams": False,
            "svg_extra_style": """
/* Color-code legend positions by layer */

/* Base layer tap: center - default dark color */
svg.keymap .tap {
    font-size: 16px;
    font-weight: bold;
}

/* Nav layer: top-right corner - blue */
svg.keymap .tr {
    fill: #2979ff;
    font-size: 11px;
}

/* Fn layer: top-left corner - red/coral */
svg.keymap .tl {
    fill: #e05050;
    font-size: 11px;
}

/* Num layer: bottom-left corner - green */
svg.keymap .bl {
    fill: #2e9e5e;
    font-size: 12px;
    font-weight: bold;
}

/* Shifted actions (morphs): top center - purple */
svg.keymap .shifted {
    fill: #9c5ec0;
    font-size: 11px;
}

/* Hold actions: bottom center - dark gray */
svg.keymap .hold {
    fill: #808890;
    font-size: 12px;
}

/* Leader sequences: bottom-right corner - orange */
svg.keymap .br {
    fill: #e67e22;
    font-size: 12px;
}

/* Ghost keys for combo diagram - very light */
rect.ghost {
    fill: #eef0f3;
    stroke: #d8dce0;
    stroke-dasharray: none;
}

/* Combo boxes styling */
rect.combo {
    fill: #d8dee9;
    stroke: #a7adba;
}
""",
        },
    }

    with open(output_path, "w") as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=200)

    print(f"Merged {num_keys_count} keys into overview YAML: {output_path}")


# Map CSS legend position classes to their fill colors (must match svg_extra_style above)
_CLASS_COLORS = {
    "tl": "#e05050",      # Fn layer - red
    "tr": "#2979ff",      # Nav layer - blue
    "bl": "#2e9e5e",      # Num layer - green
    "br": "#e67e22",      # Leader sequences - orange
    "shifted": "#9c5ec0", # Shifted - purple
    "hold": "#808890",    # Hold - dark gray
    "tap": "#24292e",     # Base tap - near-black (default)
}


def fix_glyph_fills(svg_path, output_path=None):
    """Post-process SVG to fix glyph rendering in librsvg (rsvg-convert).

    keymap-drawer wraps each fetched glyph SVG in an outer <svg id="name">
    container, producing double-nested SVGs in <defs>:

        <svg id="mdi:volume-high">          ← outer wrapper (referenced by <use>)
          <svg viewBox="0 0 24 24">         ← inner (actual glyph with <path>)
            <path d="..."/>
          </svg>
        </svg>

    librsvg doesn't reliably render the inner <svg> through <use> shadow DOM,
    and CSS fill inheritance doesn't reach the <path> elements.

    Fix: flatten the double nesting by removing the outer wrapper, transferring
    its id to the inner <svg>, and inlining fill colors on <path> elements
    based on which CSS class the <use> elements have.
    """
    with open(svg_path) as f:
        svg = f.read()

    # Build a map of glyph_id -> color from <use> elements
    glyph_colors = {}
    for match in re.finditer(r'<use\b[^>]*\bglyph\b[^>]*/>', svg):
        tag = match.group(0)
        href_match = re.search(r'href="([^"]*)"', tag)
        if not href_match:
            continue
        glyph_id = href_match.group(1).lstrip("#")
        classes = re.findall(r'class="([^"]*)"', tag)
        if not classes:
            continue
        class_list = classes[0].split()
        color = "#24292e"
        for cls in class_list:
            if cls in _CLASS_COLORS:
                color = _CLASS_COLORS[cls]
                break
        glyph_colors[glyph_id] = color

    # Flatten double-nested <svg> wrappers and inline fill on <path> elements
    for glyph_id, color in glyph_colors.items():
        # Match: <svg id="mdi:..."><svg ...viewBox...>...<path .../></svg></svg>
        pattern = re.compile(
            r'<svg\s+id="' + re.escape(glyph_id) + r'"[^>]*>\s*'
            r'<svg\b([^>]*)>(.*?)</svg>\s*'
            r'</svg>',
            re.DOTALL,
        )
        match = pattern.search(svg)
        if not match:
            continue
        inner_attrs = match.group(1)
        inner_content = match.group(2)
        # Add fill to <path> elements that don't already have one
        inner_content = re.sub(
            r'<path\b(?![^>]*\bfill=)',
            f'<path fill="{color}"',
            inner_content,
        )
        # Remove any existing id from inner attrs, add our glyph id
        inner_attrs = re.sub(r'\s*id="[^"]*"', '', inner_attrs)
        replacement = f'<svg id="{glyph_id}"{inner_attrs}>{inner_content}</svg>'
        svg = svg[:match.start()] + replacement + svg[match.end():]

    out = output_path or svg_path
    with open(out, "w") as f:
        f.write(svg)
    print(f"Fixed glyph fills in: {out}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix-svg":
        svg_path = sys.argv[2] if len(sys.argv) > 2 else "draw/overview.svg"
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        fix_glyph_fills(svg_path, output_path)
    else:
        input_path = sys.argv[1] if len(sys.argv) > 1 else "draw/base.yaml"
        output_path = sys.argv[2] if len(sys.argv) > 2 else "draw/overview.yaml"
        merge_layers(input_path, output_path)
