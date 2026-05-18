from __future__ import annotations

import numpy as np
from manim import *

from utils.plot_helpers import PALETTE


def make_generator(radius: float = 0.72, label: str = "Generator") -> VGroup:
    """Create a simplified synchronous generator symbol."""
    outer = Circle(radius=radius, color=PALETTE["electric"], stroke_width=4)
    outer.set_fill(PALETTE["panel"], opacity=1.0)
    inner = Circle(radius=radius * 0.78, color=PALETTE["electric"], stroke_width=1.3)
    inner.set_opacity(0.55)
    body = VGroup(outer, inner)
    rotor = Circle(radius=radius * 0.38, color=PALETTE["mechanical"], stroke_width=3)
    rotor.set_fill(PALETTE["background"], opacity=1.0)
    pole_a = RoundedRectangle(
        width=radius * 0.5,
        height=radius * 0.15,
        corner_radius=radius * 0.05,
        color=PALETTE["mechanical"],
        stroke_width=2.4,
    )
    pole_a.set_fill(PALETTE["mechanical"], opacity=0.55)
    pole_b = pole_a.copy().rotate(PI / 2)
    coil_left = Arc(radius=radius * 0.56, start_angle=2.25, angle=1.3, color=PALETTE["electric"], stroke_width=3)
    coil_right = Arc(radius=radius * 0.56, start_angle=-0.9, angle=1.3, color=PALETTE["electric"], stroke_width=3)
    stator_slots = VGroup()
    for index in range(12):
        angle = index * TAU / 12
        slot = Line(
            radius * 0.83 * np.array([np.cos(angle), np.sin(angle), 0]),
            radius * 0.93 * np.array([np.cos(angle), np.sin(angle), 0]),
            color=PALETTE["muted"],
            stroke_width=1.2,
        )
        slot.set_opacity(0.55)
        stator_slots.add(slot)
    name = Text(label, font_size=22, color=PALETTE["text"]).next_to(body, DOWN, buff=0.16)
    return VGroup(body, rotor, pole_a, pole_b, coil_left, coil_right, stator_slots, name)


def make_load(width: float = 1.55, height: float = 1.08, label: str = "Nonlinear\nload") -> VGroup:
    """Create a simplified electrical load block with a nonlinear mark."""
    box = Rectangle(width=width, height=height, color=PALETTE["harmonic3"], stroke_width=3)
    box.set_fill(PALETTE["panel"], opacity=1.0)
    text = Text(label, font_size=19, color=PALETTE["text"], line_spacing=0.78)
    text.move_to(box.get_center() + UP * height * 0.16)
    zigzag = VMobject(color=PALETTE["harmonic3"], stroke_width=3)
    xs = np.linspace(-width * 0.34, width * 0.34, 9)
    points = []
    for index, x in enumerate(xs):
        y = height * (-0.28 if index % 2 else -0.38)
        points.append(np.array([x, y, 0]))
    zigzag.set_points_as_corners(points)
    terminals = VGroup(
        Line(LEFT * width * 0.5, LEFT * width * 0.68, color=PALETTE["harmonic3"], stroke_width=3),
        Line(RIGHT * width * 0.5, RIGHT * width * 0.68, color=PALETTE["harmonic3"], stroke_width=3),
    )
    return VGroup(box, text, zigzag, terminals)


def make_wire_between(start: np.ndarray, end: np.ndarray, color: str | ManimColor | None = None) -> VGroup:
    """Create a clean segmented wire between two points."""
    mid_x = (start[0] + end[0]) / 2
    path = VGroup(
        Line(start, np.array([mid_x, start[1], 0])),
        Line(np.array([mid_x, start[1], 0]), np.array([mid_x, end[1], 0])),
        Line(np.array([mid_x, end[1], 0]), end),
    )
    path.set_color(color or PALETTE["electric"])
    path.set_stroke(width=3)
    return path


def make_current_arrow(start: np.ndarray, end: np.ndarray, label: str, color: str | ManimColor) -> VGroup:
    """Create an arrow indicating current flow."""
    arrow = Arrow(start, end, buff=0.05, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.12)
    text = Text(label, font_size=20, color=color).next_to(arrow, UP, buff=0.12)
    return VGroup(arrow, text)


def make_flow_dots(
    start: np.ndarray,
    end: np.ndarray,
    phase: float,
    color: str | ManimColor,
    count: int = 6,
    radius: float = 0.045,
    reverse: bool = False,
) -> VGroup:
    """Create moving dots along a straight conductor."""
    dots = VGroup()
    for index in range(count):
        alpha = (phase + index / count) % 1.0
        if reverse:
            alpha = 1.0 - alpha
        dot = Dot(interpolate(start, end, alpha), radius=radius, color=color)
        dot.set_opacity(0.35 + 0.55 * ((index + 1) / count))
        dots.add(dot)
    return dots


def make_magnetic_field_lines(radius: float = 0.95, count: int = 5) -> VGroup:
    """Create stylized field lines around a generator."""
    lines = VGroup()
    for index in range(count):
        scale = 0.72 + 0.12 * index
        line = Arc(
            radius=radius * scale,
            start_angle=-PI * 0.85,
            angle=PI * 1.7,
            color=PALETTE["electric"],
            stroke_width=max(1.4, 3 - 0.25 * index),
        )
        line.set_fill(opacity=0)
        line.set_stroke(opacity=0.65 - 0.07 * index)
        lines.add(line)
    return lines
