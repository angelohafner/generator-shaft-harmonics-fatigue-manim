from __future__ import annotations

import numpy as np
from manim import *

from utils.plot_helpers import PALETTE


def make_turbine(radius: float = 0.72, label: str = "Turbine") -> VGroup:
    """Create a simplified turbine with radial blades."""
    ring = Circle(radius=radius, color=PALETTE["mechanical"], stroke_width=4)
    ring.set_fill(PALETTE["panel"], opacity=1.0)
    hub = Circle(radius=radius * 0.22, color=PALETTE["mechanical"], stroke_width=2)
    hub.set_fill(PALETTE["mechanical"], opacity=0.35)
    blades = VGroup()
    for index in range(8):
        blade = Polygon(
            np.array([radius * 0.22, -radius * 0.055, 0]),
            np.array([radius * 0.86, 0, 0]),
            np.array([radius * 0.22, radius * 0.09, 0]),
            color=PALETTE["mechanical"],
            stroke_width=1.6,
        )
        blade.set_fill(PALETTE["mechanical"], opacity=0.45)
        blade.rotate(index * TAU / 8, about_point=ORIGIN)
        blades.add(blade)
    name = Text(label, font_size=22, color=PALETTE["text"]).next_to(ring, DOWN, buff=0.16)
    return VGroup(ring, blades, hub, name)


def make_shaft(length: float = 2.0, radius: float = 0.13) -> VGroup:
    """Create a horizontal shaft."""
    body = Rectangle(width=length, height=2 * radius, stroke_width=2, color=PALETTE["shaft"])
    body.set_fill(PALETTE["steel"], opacity=0.75)
    center_line = Line(LEFT * length / 2, RIGHT * length / 2, color=PALETTE["muted"], stroke_width=1.2)
    return VGroup(body, center_line)


def make_twisted_shaft(start: np.ndarray, end: np.ndarray, radius: float = 0.14, twist: float = 0.0) -> VGroup:
    """Create a shaft with slanted end markers to suggest torsion."""
    length = np.linalg.norm(end - start)
    midpoint = (start + end) / 2
    shaft = make_shaft(length=length, radius=radius).move_to(midpoint)
    markers = VGroup()
    for alpha in np.linspace(0.12, 0.88, 6):
        center = start + alpha * (end - start)
        marker = Line(center + UP * radius * 0.95, center + DOWN * radius * 0.95)
        marker.set_color(PALETTE["text"]).set_stroke(width=1.6, opacity=0.8)
        marker.rotate(twist * (alpha - 0.5) * 2.0, about_point=center)
        markers.add(marker)
    return VGroup(shaft, markers)


def make_cylindrical_shaft(
    start: np.ndarray,
    end: np.ndarray,
    radius: float = 0.14,
    twist: float = 0.0,
    bands: int = 8,
) -> VGroup:
    """Create a polished cylindrical horizontal shaft with torsion bands."""
    length = np.linalg.norm(end - start)
    center = (start + end) / 2
    height = 2 * radius

    body = RoundedRectangle(
        width=length,
        height=height,
        corner_radius=radius * 0.92,
        color=PALETTE["shaft"],
        stroke_width=2.4,
    )
    body.set_fill(PALETTE["steel"], opacity=0.9)
    body.move_to(center)

    left_cap = Ellipse(width=height * 0.55, height=height * 1.08, color=PALETTE["shaft"], stroke_width=2.2)
    left_cap.set_fill(PALETTE["panel"], opacity=0.72).move_to(start)
    right_cap = left_cap.copy().move_to(end)

    highlight = Line(
        start + UP * radius * 0.48,
        end + UP * radius * 0.48,
        color=PALETTE["text"],
        stroke_width=2.0,
    )
    highlight.set_opacity(0.25)
    shadow = Line(
        start + DOWN * radius * 0.58,
        end + DOWN * radius * 0.58,
        color=PALETTE["background"],
        stroke_width=3.0,
    )
    shadow.set_opacity(0.34)

    markers = VGroup()
    for alpha in np.linspace(0.12, 0.88, bands):
        marker_center = interpolate(start, end, alpha)
        marker = Line(
            marker_center + UP * radius * 0.88,
            marker_center + DOWN * radius * 0.88,
            color=PALETTE["muted"],
            stroke_width=1.45,
        )
        marker.rotate(twist * (alpha - 0.5) * 2.0, about_point=marker_center)
        marker.set_opacity(0.7)
        markers.add(marker)

    return VGroup(body, left_cap, right_cap, highlight, shadow, markers)


def make_torsion_wave(
    start: np.ndarray,
    end: np.ndarray,
    amplitude: float = 0.12,
    turns: float = 6.0,
    phase: float = 0.0,
    color: str | ManimColor | None = None,
) -> VMobject:
    """Create a vibration wave spanning the full shaft length."""
    color = color or PALETTE["mechanical"]
    points = []
    for alpha in np.linspace(0.0, 1.0, 180):
        x = interpolate(start, end, alpha)
        envelope = np.sin(PI * alpha)
        y_offset = amplitude * envelope * np.sin(TAU * turns * alpha + phase)
        points.append(x + UP * y_offset)

    wave = VMobject(color=color, stroke_width=4)
    wave.set_points_smoothly(points)
    return wave


def make_torsional_spring(length: float = 2.1, amplitude: float = 0.22, turns: int = 7) -> VMobject:
    """Create a horizontal torsional spring as a sinusoidal coil."""
    x_values = np.linspace(-length / 2, length / 2, 120)
    points = [
        np.array([x, amplitude * np.sin(TAU * turns * (x + length / 2) / length), 0])
        for x in x_values
    ]
    spring = VMobject(color=PALETTE["mechanical"], stroke_width=4)
    spring.set_points_smoothly(points)
    return spring


def make_disc(radius: float = 0.52, label: str = "", marker_angle: float = 0.0) -> VGroup:
    """Create a rotor disk with a visible angular marker."""
    disk = Circle(radius=radius, color=PALETTE["shaft"], stroke_width=4)
    disk.set_fill(PALETTE["panel"], opacity=1.0)
    marker = Line(ORIGIN, radius * 0.82 * RIGHT, color=PALETTE["mechanical"], stroke_width=4)
    marker.rotate(marker_angle, about_point=ORIGIN)
    dot = Dot(ORIGIN, radius=radius * 0.08, color=PALETTE["mechanical"])
    group = VGroup(disk, marker, dot)
    if label:
        text = Text(label, font_size=20, color=PALETTE["text"]).next_to(disk, DOWN, buff=0.12)
        group.add(text)
    return group


def make_torque_arrow(
    center: np.ndarray,
    radius: float = 0.82,
    color: str | ManimColor = WHITE,
    clockwise: bool = False,
    label: str = "",
) -> VGroup:
    """Create a curved arrow representing torque."""
    if clockwise:
        start_angle = 0.75 * PI
        arc_angle = -PI * 0.95
    else:
        start_angle = -0.35 * PI
        arc_angle = PI * 0.95

    end_angle = start_angle + arc_angle
    arc = Arc(
        radius=radius,
        start_angle=start_angle,
        angle=arc_angle,
        arc_center=center,
        color=color,
        stroke_width=4,
    )
    tip_position = center + radius * np.array([np.cos(end_angle), np.sin(end_angle), 0])
    tangent_angle = end_angle + (PI / 2 if arc_angle > 0 else -PI / 2)
    tip = Triangle(color=color, stroke_width=0)
    tip.set_fill(color, opacity=1.0)
    tip.set_height(0.18)
    tip.rotate(tangent_angle - PI / 2)
    tip.move_to(tip_position)

    group = VGroup(arc, tip)
    if label:
        text = MathTex(label, color=color, font_size=32).next_to(arc, UP if not clockwise else DOWN, buff=0.05)
        group.add(text)
    return group


def make_crack(length: float = 0.35, color: str | ManimColor = None) -> VMobject:
    """Create a small zigzag crack for fatigue visualization."""
    color = color or PALETTE["danger"]
    points = [
        np.array([0.0, 0.0, 0.0]),
        np.array([length * 0.18, length * 0.15, 0.0]),
        np.array([length * 0.32, -length * 0.08, 0.0]),
        np.array([length * 0.52, length * 0.18, 0.0]),
        np.array([length * 0.72, -length * 0.03, 0.0]),
        np.array([length, length * 0.22, 0.0]),
    ]
    crack = VMobject(color=color, stroke_width=4)
    crack.set_points_as_corners(points)
    return crack
