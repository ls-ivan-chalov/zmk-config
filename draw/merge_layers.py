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
        "Prev Win": "PWin",
        "Next Win": "NWin",
        "Prev Desk": "PDsk",
        "Next Desk": "NDsk",
        "Alt+F4": "AltF4",
        "Pin App": "PnApp",
        "Pin Win": "PnWin",
        "Alt+`": "Alt`",
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

        # Top-right: Nav layer (skip trans/held)
        nav_tap = get_tap(nav_keys[i]) if i < len(nav_keys) else ""
        nav_hold = get_hold(nav_keys[i]) if i < len(nav_keys) else ""
        # For nav, show the tap action. If it's a sticky mod, show that.
        if nav_tap and not is_trans(nav_keys[i]) and not is_held(nav_keys[i]):
            out["tr"] = shorten_legend(nav_tap)

        # Top-left: Fn layer (skip trans/held)
        fn_tap = get_tap(fn_keys[i]) if i < len(fn_keys) else ""
        if fn_tap and not is_trans(fn_keys[i]) and not is_held(fn_keys[i]):
            out["tl"] = shorten_legend(fn_tap)

        # Bottom-left: Num layer (skip trans/held)
        num_tap = get_tap(num_keys[i]) if i < len(num_keys) else ""
        if num_tap and not is_trans(num_keys[i]) and not is_held(num_keys[i]):
            out["bl"] = shorten_legend(num_tap)

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
            "footer_text": '<tspan style="fill: #24292e; font-weight: bold">Base</tspan>  <tspan style="fill: #e05050">Fn</tspan>  <tspan style="fill: #2979ff">Nav</tspan>  <tspan style="fill: #2e9e5e">Num</tspan>  <tspan style="fill: #9c5ec0">Shifted</tspan>  <tspan style="fill: #808890">Hold</tspan>',
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


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "draw/base.yaml"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "draw/overview.yaml"
    merge_layers(input_path, output_path)
