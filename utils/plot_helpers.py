from __future__ import annotations

import numpy as np
from manim import *


PALETTE = {
    "background": "#0F172A",
    "panel": "#162033",
    "text": "#F8FAFC",
    "muted": "#CBD5E1",
    "electric": "#38BDF8",
    "harmonic3": "#F59E0B",
    "harmonic5": "#EF4444",
    "sum": "#22C55E",
    "mechanical": "#A3E635",
    "shaft": "#94A3B8",
    "steel": "#64748B",
    "danger": "#F97316",
    "fatigue": "#FB7185",
    "resonance": "#FACC15",
}


def configure_scene(scene: Scene) -> None:
    """Apply a common visual configuration to each scene."""
    scene.camera.background_color = PALETTE["background"]


def make_title(text: str, font_size: int = 36) -> Text:
    """Create a consistently styled scene title."""
    return Text(text, font_size=font_size, color=PALETTE["text"]).to_edge(UP)


def make_note(text: str, font_size: int = 24, color: str | ManimColor | None = None) -> Text:
    """Create a compact explanatory note."""
    return Text(
        text,
        font_size=font_size,
        color=color or PALETTE["muted"],
        line_spacing=0.85,
    )


def make_wave_axes(
    x_length: float = 7.0,
    y_length: float = 2.2,
    x_range: list[float] | None = None,
    y_range: list[float] | None = None,
) -> Axes:
    """Create clean axes for time-domain waveforms."""
    return Axes(
        x_range=x_range or [0, TAU, PI / 2],
        y_range=y_range or [-1.5, 1.5, 0.5],
        x_length=x_length,
        y_length=y_length,
        tips=False,
        axis_config={
            "color": PALETTE["muted"],
            "stroke_width": 2,
            "include_numbers": False,
        },
    )


def waveform_component(kind: str):
    """Return a waveform function used in the harmonic scenes."""
    if kind == "fundamental":
        return lambda t: np.sin(t)
    if kind == "third":
        return lambda t: 0.25 * np.sin(3 * t + 0.4)
    if kind == "fifth":
        return lambda t: 0.15 * np.sin(5 * t - 0.2)
    if kind == "sum":
        return lambda t: (
            np.sin(t)
            + 0.25 * np.sin(3 * t + 0.4)
            + 0.15 * np.sin(5 * t - 0.2)
        )
    raise ValueError(f"Unknown waveform kind: {kind}")


def make_component_label(text: str, color: str | ManimColor, font_size: int = 22) -> VGroup:
    """Create a line sample plus label for graph legends."""
    sample = Line(LEFT * 0.28, RIGHT * 0.28, color=color, stroke_width=5)
    label = Text(text, font_size=font_size, color=PALETTE["text"])
    return VGroup(sample, label).arrange(RIGHT, buff=0.12)


def amplitude_response(omega: float, k: float = 1.0, j: float = 1.0, d: float = 0.16) -> float:
    """Compute a normalized didactic frequency-response amplitude."""
    return 1.0 / np.sqrt((k - j * omega**2) ** 2 + (d * omega) ** 2)


def make_resonance_plot(width: float = 5.0, height: float = 2.8) -> tuple[Axes, VMobject, VGroup]:
    """Create a simple amplitude-versus-frequency resonance plot."""
    axes = Axes(
        x_range=[0, 2.0, 0.5],
        y_range=[0, 7.0, 2],
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={
            "color": PALETTE["muted"],
            "stroke_width": 2,
            "include_numbers": False,
        },
    )
    curve = axes.plot(
        lambda w: min(amplitude_response(w), 6.8),
        x_range=[0.05, 2.0, 0.01],
        color=PALETTE["resonance"],
        stroke_width=4,
    )
    x_label = Text("frequency", font_size=18, color=PALETTE["muted"]).next_to(axes, DOWN, buff=0.2)
    y_label = Text("amplitude", font_size=18, color=PALETTE["muted"]).rotate(PI / 2)
    y_label.next_to(axes, LEFT, buff=0.2)
    peak = Dot(axes.c2p(1.0, min(amplitude_response(1.0), 6.8)), color=PALETTE["danger"])
    peak_label = Text("resonance", font_size=18, color=PALETTE["danger"]).next_to(peak, UP, buff=0.12)
    labels = VGroup(x_label, y_label, peak, peak_label)
    return axes, curve, labels


def make_sn_curve(width: float = 4.2, height: float = 2.6) -> tuple[Axes, VMobject, VGroup]:
    """Create a simplified S-N curve with linear axes for readability."""
    axes = Axes(
        x_range=[0, 6, 1],
        y_range=[0, 1.2, 0.3],
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={
            "color": PALETTE["muted"],
            "stroke_width": 2,
            "include_numbers": False,
        },
    )
    curve = axes.plot(
        lambda x: 0.9 / (1 + 0.35 * x) + 0.12,
        x_range=[0.1, 6, 0.05],
        color=PALETTE["fatigue"],
        stroke_width=4,
    )
    x_label = VGroup(
        Text("cycles", font_size=18, color=PALETTE["muted"]),
        MathTex(r"N", font_size=22, color=PALETTE["muted"]),
    ).arrange(RIGHT, buff=0.08).next_to(axes, DOWN, buff=0.18)
    y_label = Text("stress", font_size=18, color=PALETTE["muted"]).rotate(PI / 2)
    y_label.next_to(axes, LEFT, buff=0.18)
    title = Text("Simplified S-N curve", font_size=21, color=PALETTE["text"]).next_to(axes, UP, buff=0.18)
    return axes, curve, VGroup(x_label, y_label, title)


def make_damage_bar(width: float = 3.2, height: float = 0.28) -> tuple[RoundedRectangle, Rectangle]:
    """Create background and fill objects for an accumulated damage bar."""
    background = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.06,
        color=PALETTE["muted"],
        stroke_width=2,
    ).set_fill(PALETTE["panel"], opacity=1.0)
    fill = Rectangle(
        width=0.01,
        height=height * 0.75,
        stroke_width=0,
        fill_color=PALETTE["danger"],
        fill_opacity=1.0,
    )
    fill.align_to(background, LEFT)
    return background, fill


def make_simple_table(
    headers: list[str],
    rows: list[list[str]],
    col_widths: list[float],
    row_height: float = 0.55,
    font_size: int = 20,
) -> VGroup:
    """Create a lightweight vector table using rectangles and Text."""
    table = VGroup()
    all_rows = [headers, *rows]
    total_width = sum(col_widths)
    start_x = -total_width / 2
    start_y = row_height * len(all_rows) / 2

    for row_index, row in enumerate(all_rows):
        y = start_y - row_height * (row_index + 0.5)
        x = start_x
        for col_index, cell in enumerate(row):
            width = col_widths[col_index]
            rect = Rectangle(width=width, height=row_height, stroke_width=1.4)
            rect.set_stroke(PALETTE["muted"], opacity=0.8)
            rect.set_fill(PALETTE["panel"] if row_index == 0 else PALETTE["background"], opacity=0.95)
            rect.move_to([x + width / 2, y, 0])
            text = Text(
                cell,
                font_size=font_size if row_index else font_size + 1,
                color=PALETTE["text"] if row_index == 0 else PALETTE["muted"],
                line_spacing=0.8,
            )
            text.move_to(rect.get_center())
            text.set_max_width(width * 0.88)
            table.add(VGroup(rect, text))
            x += width
    return table
