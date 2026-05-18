import numpy as np
from manim import *

from utils.mechanical_shapes import make_crack, make_torque_arrow
from utils.plot_helpers import (
    PALETTE,
    configure_scene,
    make_damage_bar,
    make_note,
    make_sn_curve,
    make_title,
    make_wave_axes,
)


def make_fatigue_shaft(start: np.ndarray, end: np.ndarray, radius: float, twist: float, phase: float = 0.0) -> VGroup:
    """Create a polished animated cylindrical shaft with torsion bands."""
    length = np.linalg.norm(end - start)
    center = (start + end) / 2
    height = 2 * radius

    body = RoundedRectangle(
        width=length,
        height=height,
        corner_radius=height * 0.45,
        color=PALETTE["shaft"],
        stroke_width=2.5,
    )
    body.set_fill(PALETTE["steel"], opacity=0.88)
    body.move_to(center)

    upper_skin = RoundedRectangle(
        width=length * 0.98,
        height=height * 0.42,
        corner_radius=height * 0.2,
        stroke_width=0,
        fill_color=PALETTE["shaft"],
        fill_opacity=0.28,
    )
    upper_skin.move_to(center + UP * radius * 0.28)
    lower_skin = RoundedRectangle(
        width=length * 0.98,
        height=height * 0.34,
        corner_radius=height * 0.16,
        stroke_width=0,
        fill_color=PALETTE["background"],
        fill_opacity=0.16,
    )
    lower_skin.move_to(center + DOWN * radius * 0.34)

    highlight = Line(
        center + LEFT * length / 2 + UP * radius * 0.45,
        center + RIGHT * length / 2 + UP * radius * 0.45,
        color=PALETTE["text"],
        stroke_width=2.2,
    )
    highlight.set_opacity(0.3 + 0.08 * np.sin(phase) ** 2)
    shadow = Line(
        center + LEFT * length / 2 + DOWN * radius * 0.58,
        center + RIGHT * length / 2 + DOWN * radius * 0.58,
        color=PALETTE["background"],
        stroke_width=3.6,
    )
    shadow.set_opacity(0.35)

    caps = VGroup()
    for index, point in enumerate([start, end]):
        cap = Ellipse(width=height * 0.72, height=height * 1.22, color=PALETTE["shaft"], stroke_width=2.8)
        cap.set_fill(PALETTE["panel"], opacity=0.72).move_to(point)
        inner_cap = Ellipse(width=height * 0.45, height=height * 0.9, color=PALETTE["muted"], stroke_width=1.3)
        inner_cap.set_opacity(0.3 + 0.12 * np.sin(phase + index * PI / 2) ** 2).move_to(point)
        rim_glow = Arc(
            radius=height * 0.63,
            start_angle=-PI / 2,
            angle=PI,
            color=PALETTE["text"],
            stroke_width=1.8,
        )
        rim_glow.set_width(height * 0.35)
        rim_glow.set_height(height * 1.02)
        rim_glow.set_opacity(0.18 + 0.12 * np.sin(phase + index) ** 2).move_to(point + UP * radius * 0.02)
        caps.add(cap, inner_cap, rim_glow)

    bands = VGroup()
    for alpha in np.linspace(0.08, 0.92, 13):
        x = interpolate(start, end, alpha)
        band = Line(
            x + UP * radius * 0.92,
            x + DOWN * radius * 0.92,
            color=PALETTE["muted"],
            stroke_width=1.55,
        )
        band.rotate(twist * (alpha - 0.5) * 2.3 + 0.12 * np.sin(phase + TAU * alpha), about_point=x)
        band.set_opacity(0.48 + 0.3 * np.sin(phase + TAU * alpha) ** 2)
        bands.add(band)

    glints = VGroup()
    for index, offset in enumerate([0.02, 0.3, 0.58]):
        alpha = 0.08 + np.mod(0.07 * phase + offset, 0.84)
        x = interpolate(start, end, alpha)
        glint = Line(
            x + LEFT * 0.2 + UP * radius * 0.54,
            x + RIGHT * 0.28 + UP * radius * 0.54,
            color=PALETTE["text"],
            stroke_width=2.1,
        )
        glint.set_opacity(0.12 + 0.18 * np.sin(phase * 1.4 + index) ** 2)
        glints.add(glint)

    stress_points = []
    for alpha in np.linspace(0.02, 0.98, 120):
        point = interpolate(start, end, alpha)
        envelope = 0.35 + 0.65 * np.sin(PI * alpha)
        y_offset = radius * 0.42 * envelope * np.sin(TAU * 2.8 * alpha + 1.25 * phase)
        stress_points.append(point + UP * y_offset)
    stress_ribbon = VMobject(color=PALETTE["fatigue"], stroke_width=2.8)
    stress_ribbon.set_points_smoothly(stress_points)
    stress_ribbon.set_opacity(0.62)

    return VGroup(body, upper_skin, lower_skin, caps, highlight, shadow, bands, glints, stress_ribbon)


class FadigaEixoGerador(Scene):
    def construct(self):
        configure_scene(self)

        title = make_title("Shaft fatigue buildup", font_size=34)
        stress_eq = MathTex(r"\tau=\frac{T r}{J_p}", font_size=38, color=PALETTE["text"])
        stress_eq.move_to(LEFT * 1.0 + UP * 2.45)
        miner_eq = MathTex(r"D=\sum \frac{n_i}{N_i}", font_size=38, color=PALETTE["text"])
        n_definition = VGroup(
            MathTex(r"n_i", font_size=22, color=PALETTE["text"]),
            Text(": applied cycles", font_size=17, color=PALETTE["muted"]),
        ).arrange(RIGHT, buff=0.08)
        n_limit_definition = VGroup(
            MathTex(r"N_i", font_size=22, color=PALETTE["text"]),
            Text(": cycles to failure", font_size=17, color=PALETTE["muted"]),
        ).arrange(RIGHT, buff=0.08)
        miner_note = VGroup(n_definition, n_limit_definition).arrange(DOWN, aligned_edge=LEFT, buff=0.11)
        miner_group = VGroup(miner_eq, miner_note).arrange(DOWN, buff=0.1)
        miner_group.move_to(RIGHT * 3.55 + UP * 2.38)

        damage = ValueTracker(0.0)
        cycle_count = ValueTracker(0.0)
        phase = ValueTracker(0.0)

        left = LEFT * 4.25 + UP * 1.18
        right = RIGHT * 0.85 + UP * 1.18
        shaft = always_redraw(
            lambda: make_fatigue_shaft(
                left,
                right,
                radius=0.2,
                twist=0.88 * np.sin(phase.get_value()),
                phase=phase.get_value(),
            )
        )
        torque_left = always_redraw(
            lambda: make_torque_arrow(
                left + LEFT * 0.12,
                radius=0.58 + 0.08 * np.sin(phase.get_value()),
                color=PALETTE["mechanical"],
                clockwise=False,
                label="",
            )
        )
        torque_right = always_redraw(
            lambda: make_torque_arrow(
                right + RIGHT * 0.12,
                radius=0.58 - 0.08 * np.sin(phase.get_value()),
                color=PALETTE["electric"],
                clockwise=True,
                label="",
            )
        )
        tm_label = MathTex(r"T_m", color=PALETTE["mechanical"], font_size=30).next_to(torque_left, UP, buff=0.05)
        te_label = MathTex(r"T_e(t)", color=PALETTE["electric"], font_size=30).next_to(torque_right, DOWN, buff=0.02)

        crack = always_redraw(
            lambda: make_crack(length=0.08 + 0.72 * damage.get_value())
            .rotate(PI / 2)
            .move_to(LEFT * 1.05 + UP * (1.18 + 0.12 * damage.get_value()))
            .set_z_index(10)
        )

        cycles_label = Text("cycles", font_size=21, color=PALETTE["muted"]).move_to(LEFT * 5.35 + UP * 2.45)
        cycles_number = DecimalNumber(0, num_decimal_places=0, color=PALETTE["text"], font_size=34)
        cycles_number.add_updater(lambda mob: mob.set_value(cycle_count.get_value()))
        cycles_number.next_to(cycles_label, RIGHT, buff=0.18)

        bar_background, bar_fill = make_damage_bar(width=3.25, height=0.33)
        bar_group = VGroup(bar_background, bar_fill).move_to(RIGHT * 4.95 + UP * 1.28)
        bar_title = Text("accumulated damage", font_size=18, color=PALETTE["muted"]).next_to(bar_background, DOWN, buff=0.08)
        bar_fill.add_updater(
            lambda mob: mob.become(
                Rectangle(
                    width=max(0.01, 3.25 * damage.get_value()),
                    height=0.33 * 0.75,
                    stroke_width=0,
                    fill_color=PALETTE["danger"],
                    fill_opacity=1.0,
                )
                .align_to(bar_background, LEFT)
                .move_to(bar_background.get_left() + RIGHT * max(0.01, 3.25 * damage.get_value()) / 2)
            )
        )

        stress_axes = make_wave_axes(x_length=5.2, y_length=2.15, x_range=[0, 4 * PI, PI], y_range=[-1.2, 1.2, 0.4])
        stress_axes.move_to(LEFT * 3.05 + DOWN * 1.65)
        stress_curve = stress_axes.plot(lambda x: 0.85 * np.sin(x), x_range=[0, 4 * PI, 0.03], color=PALETTE["fatigue"], stroke_width=4)
        stress_title = Text("repeated torsional stress", font_size=21, color=PALETTE["text"]).next_to(stress_axes, UP, buff=0.16)
        stress_x_label = VGroup(
            Text("time", font_size=18, color=PALETTE["muted"]),
            MathTex(r"t", font_size=22, color=PALETTE["muted"]),
        ).arrange(RIGHT, buff=0.08).next_to(stress_axes, DOWN, buff=0.2)
        stress_y_label = MathTex(r"\tau(t)", font_size=30, color=PALETTE["muted"]).rotate(PI / 2)
        stress_y_label.next_to(stress_axes, LEFT, buff=0.25)

        sn_axes, sn_curve, _ = make_sn_curve(width=4.25, height=2.45)
        sn_axes.move_to(RIGHT * 3.05 + DOWN * 1.63)
        sn_curve = sn_axes.plot(
            lambda x: 0.9 / (1 + 0.35 * x) + 0.12,
            x_range=[0.1, 6, 0.05],
            color=PALETTE["fatigue"],
            stroke_width=4,
        )
        sn_title = VGroup(
            Text("Simplified", font_size=20, color=PALETTE["text"]),
            Text("S-N curve", font_size=20, color=PALETTE["text"]),
        ).arrange(RIGHT, buff=0.1).next_to(sn_axes, UP, buff=0.18)
        sn_x_label = VGroup(
            Text("cycles", font_size=18, color=PALETTE["muted"]),
            MathTex(r"N", font_size=22, color=PALETTE["muted"]),
        ).arrange(RIGHT, buff=0.08).next_to(sn_axes, DOWN, buff=0.22)
        sn_y_label = Text("stress amplitude", font_size=16, color=PALETTE["muted"]).rotate(PI / 2)
        sn_y_label.next_to(sn_axes, LEFT, buff=0.28)
        sn_labels = VGroup(sn_title, sn_x_label, sn_y_label)

        warning = make_note(
            "Fatigue accumulates: many cycles can matter more than one event.",
            font_size=23,
            color=PALETTE["text"],
        ).to_edge(DOWN, buff=0.24)

        self.play(Write(title), Write(stress_eq))
        self.play(
            FadeIn(shaft),
            FadeIn(torque_left),
            FadeIn(torque_right),
            FadeIn(tm_label),
            FadeIn(te_label),
            FadeIn(cycles_label),
            FadeIn(cycles_number),
        )
        self.play(Create(stress_axes), FadeIn(stress_title), FadeIn(stress_x_label), FadeIn(stress_y_label), Create(stress_curve))
        self.play(phase.animate.set_value(6 * PI), cycle_count.animate.set_value(30000), run_time=3.0, rate_func=linear)
        self.play(ReplacementTransform(stress_eq.copy(), miner_eq), FadeIn(miner_note), FadeIn(bar_title), FadeIn(bar_background), FadeIn(bar_fill))
        self.play(Create(sn_axes), Create(sn_curve), FadeIn(sn_labels), FadeIn(warning, shift=UP * 0.1))
        self.play(
            phase.animate.set_value(14 * PI),
            cycle_count.animate.set_value(120000),
            damage.animate.set_value(0.86),
            run_time=5.0,
            rate_func=linear,
        )
        self.play(FadeIn(crack), run_time=0.7)
        self.wait(1.1)


def make_small_wave(width: float, height: float, color: str | ManimColor, distorted: bool = False) -> VMobject:
    """Create a compact waveform icon."""
    points = []
    for alpha in np.linspace(0, 1, 36):
        x = width * (alpha - 0.5)
        t = TAU * alpha
        y = height * 0.36 * np.sin(t)
        if distorted:
            y += height * 0.12 * np.sin(3 * t + 0.5)
        points.append(np.array([x, y, 0.0]))
    wave = VMobject(color=color, stroke_width=3)
    wave.set_points_smoothly(points)
    return wave


def make_harmonics_icon() -> VGroup:
    """Create an icon for distorted current."""
    axis = Line(LEFT * 0.5, RIGHT * 0.5, color=PALETTE["muted"], stroke_width=1.5)
    ideal = make_small_wave(1.0, 0.48, PALETTE["electric"], distorted=False).shift(UP * 0.12)
    distorted = make_small_wave(1.0, 0.48, PALETTE["sum"], distorted=True).shift(DOWN * 0.12)
    return VGroup(axis, ideal, distorted)


def make_torque_pulse_icon() -> VGroup:
    """Create an icon for pulsating electromagnetic torque."""
    rotor = Circle(radius=0.34, color=PALETTE["electric"], stroke_width=3)
    rotor.set_fill(PALETTE["panel"], opacity=0.85)
    hub = Dot(radius=0.05, color=PALETTE["mechanical"])
    pulse = make_torque_arrow(ORIGIN, radius=0.48, color=PALETTE["electric"], clockwise=False, label="")
    pulse.set_opacity(0.9)
    return VGroup(rotor, hub, pulse)


def make_resonance_icon() -> VGroup:
    """Create an icon for resonance amplification."""
    x_axis = Line(LEFT * 0.52, RIGHT * 0.55, color=PALETTE["muted"], stroke_width=1.7)
    y_axis = Line(LEFT * 0.52, LEFT * 0.52 + UP * 0.72, color=PALETTE["muted"], stroke_width=1.7)
    points = []
    for x in np.linspace(-0.45, 0.45, 34):
        y = 0.12 + 0.62 / (1 + 34 * x * x)
        points.append(np.array([x, y - 0.36, 0.0]))
    peak = VMobject(color=PALETTE["resonance"], stroke_width=3.2)
    peak.set_points_smoothly(points)
    marker = DashedLine(UP * 0.34, DOWN * 0.42, color=PALETTE["electric"], stroke_width=1.8, dash_length=0.08)
    label = MathTex(r"f_n", font_size=20, color=PALETTE["resonance"]).move_to(RIGHT * 0.36 + UP * 0.38)
    return VGroup(x_axis, y_axis, peak, marker, label)


def make_cycle_stress_icon() -> VGroup:
    """Create an icon for repeated stress cycles."""
    axis = Line(LEFT * 0.55, RIGHT * 0.55, color=PALETTE["muted"], stroke_width=1.5)
    wave = make_small_wave(1.08, 0.78, PALETTE["fatigue"], distorted=False)
    tau = MathTex(r"\tau(t)", font_size=18, color=PALETTE["fatigue"]).move_to(LEFT * 0.52 + UP * 0.35)
    return VGroup(axis, wave, tau)


def make_fatigue_icon() -> VGroup:
    """Create an icon for shaft fatigue and crack growth."""
    shaft = make_fatigue_shaft(LEFT * 0.55, RIGHT * 0.55, radius=0.11, twist=0.5)
    crack = make_crack(length=0.34, color=PALETTE["danger"]).rotate(PI / 2).move_to(RIGHT * 0.12 + UP * 0.04)
    dots = VGroup(
        Dot(LEFT * 0.34 + UP * 0.34, radius=0.025, color=PALETTE["fatigue"]),
        Dot(LEFT * 0.12 + UP * 0.42, radius=0.025, color=PALETTE["fatigue"]),
        Dot(RIGHT * 0.12 + UP * 0.34, radius=0.025, color=PALETTE["fatigue"]),
    )
    return VGroup(shaft, crack, dots)


def make_icon_node(label: str, icon: Mobject, color: str | ManimColor) -> VGroup:
    """Create a small visual node for the conclusion flow."""
    box = RoundedRectangle(width=1.92, height=1.84, corner_radius=0.08, color=color, stroke_width=2.0)
    box.set_fill(PALETTE["panel"], opacity=0.95)
    icon = icon.copy()
    icon.scale_to_fit_width(1.18)
    if icon.height > 0.76:
        icon.scale_to_fit_height(0.76)
    icon.move_to(box.get_center() + UP * 0.36)
    text = Text(label, font_size=17.2, color=PALETTE["text"], line_spacing=0.9)
    text.set_max_width(1.62)
    text.next_to(icon, DOWN, buff=0.2)
    return VGroup(box, icon, text)


def make_mitigation_icon(kind: str, label: str) -> VGroup:
    """Create a compact mitigation pictogram with a short label."""
    if kind == "modes":
        icon = make_resonance_icon().scale(0.62)
    elif kind == "filter":
        funnel = Polygon(LEFT * 0.38 + UP * 0.24, RIGHT * 0.38 + UP * 0.24, RIGHT * 0.12 + DOWN * 0.05, RIGHT * 0.12 + DOWN * 0.34, LEFT * 0.12 + DOWN * 0.34, LEFT * 0.12 + DOWN * 0.05)
        funnel.set_stroke(PALETTE["electric"], width=2.3).set_fill(PALETTE["panel"], opacity=0.8)
        ripple = make_small_wave(0.72, 0.36, PALETTE["sum"], distorted=True).shift(UP * 0.38)
        icon = VGroup(funnel, ripple)
    elif kind == "protect":
        shield = Polygon(UP * 0.38, RIGHT * 0.34 + UP * 0.18, RIGHT * 0.24 + DOWN * 0.32, ORIGIN + DOWN * 0.5, LEFT * 0.24 + DOWN * 0.32, LEFT * 0.34 + UP * 0.18)
        shield.set_stroke(PALETTE["mechanical"], width=2.5).set_fill(PALETTE["panel"], opacity=0.8)
        bolt = VMobject(color=PALETTE["resonance"], stroke_width=3)
        bolt.set_points_as_corners([UP * 0.24 + LEFT * 0.04, DOWN * 0.02 + RIGHT * 0.08, DOWN * 0.02 + LEFT * 0.02, DOWN * 0.28 + RIGHT * 0.02])
        icon = VGroup(shield, bolt)
    elif kind == "monitor":
        screen = RoundedRectangle(width=0.86, height=0.55, corner_radius=0.04, color=PALETTE["electric"], stroke_width=2.2)
        screen.set_fill(PALETTE["panel"], opacity=0.82)
        wave = make_small_wave(0.62, 0.34, PALETTE["fatigue"], distorted=False)
        stand = VGroup(Line(DOWN * 0.28, DOWN * 0.44, color=PALETTE["muted"], stroke_width=2), Line(LEFT * 0.26 + DOWN * 0.44, RIGHT * 0.26 + DOWN * 0.44, color=PALETTE["muted"], stroke_width=2))
        icon = VGroup(screen, wave, stand)
    elif kind == "control":
        lines = VGroup()
        for y, x in [(0.26, -0.18), (0.0, 0.18), (-0.26, -0.02)]:
            line = Line(LEFT * 0.42 + UP * y, RIGHT * 0.42 + UP * y, color=PALETTE["muted"], stroke_width=2)
            knob = Dot(np.array([x, y, 0.0]), radius=0.05, color=PALETTE["electric"])
            lines.add(VGroup(line, knob))
        icon = lines
    else:
        icon = make_fatigue_icon().scale(0.62)

    text = Text(label, font_size=17, color=PALETTE["muted"])
    text.set_max_width(1.65)
    icon.scale_to_fit_height(0.78)
    return VGroup(icon, text).arrange(DOWN, buff=0.13)


class Conclusao(Scene):
    def construct(self):
        configure_scene(self)

        title = make_title("Technical conclusion", font_size=42)

        nodes = VGroup(
            make_icon_node("Harmonics", make_harmonics_icon(), PALETTE["harmonic3"]),
            make_icon_node("Torque\npulses", make_torque_pulse_icon(), PALETTE["electric"]),
            make_icon_node("Resonance", make_resonance_icon(), PALETTE["resonance"]),
            make_icon_node("Stress\ncycles", make_cycle_stress_icon(), PALETTE["fatigue"]),
            make_icon_node("Fatigue", make_fatigue_icon(), PALETTE["danger"]),
        )
        for node, x_pos in zip(nodes, np.linspace(-5.55, 5.55, len(nodes))):
            node.move_to(np.array([x_pos, 1.54, 0.0]))

        arrows = VGroup()
        for left_node, right_node in zip(nodes[:-1], nodes[1:]):
            arrows.add(
                Arrow(
                    left_node.get_right() + RIGHT * 0.04,
                    right_node.get_left() + LEFT * 0.04,
                    buff=0.0,
                    color=PALETTE["muted"],
                    stroke_width=2.2,
                    max_tip_length_to_length_ratio=0.22,
                )
            )

        caution_font_size = 28
        caution_sentence = VGroup(
            Text("An", font_size=caution_font_size, color=PALETTE["text"]),
            Text("isolated", font_size=caution_font_size, color=PALETTE["text"]),
            Text("harmonic", font_size=caution_font_size, color=PALETTE["text"]),
            Text("does", font_size=caution_font_size, color=PALETTE["text"]),
            Text("not", font_size=caution_font_size, color=PALETTE["text"]),
            Text("determine", font_size=caution_font_size, color=PALETTE["text"]),
            Text("failure.", font_size=caution_font_size, color=PALETTE["text"]),
        ).arrange(RIGHT, buff=0.13)

        message = VGroup(
            caution_sentence,
            VGroup(
                Text("Risk increases with", font_size=23, color=PALETTE["muted"]),
                MathTex(r"A_h,\ f_{torque}\approx f_n,\ \zeta,\ t,\ D", font_size=35, color=PALETTE["resonance"]),
            ).arrange(RIGHT, buff=0.22),
        ).arrange(DOWN, buff=0.14)
        message.move_to(DOWN * 0.25)

        mitigation_title = Text("Mitigation", font_size=40, color=PALETTE["text"])
        mitigation_items = VGroup(
            make_mitigation_icon("modes", "modes"),
            make_mitigation_icon("filter", "filters"),
            make_mitigation_icon("protect", "protection"),
            make_mitigation_icon("monitor", "monitoring"),
            make_mitigation_icon("control", "control"),
            make_mitigation_icon("fatigue", "fatigue"),
        )
        mitigation_y = -2.62
        for item, x_pos in zip(mitigation_items, np.linspace(-5.85, 5.85, len(mitigation_items))):
            item.move_to(np.array([x_pos, mitigation_y, 0.0]))
        mitigation_title.move_to(UP * -1.18)
        mitigation_group = VGroup(mitigation_title, mitigation_items)

        self.play(Write(title))
        self.play(LaggedStart(*[FadeIn(node, shift=UP * 0.1) for node in nodes], lag_ratio=0.08), Create(arrows))
        self.play(FadeIn(message, shift=UP * 0.12))
        self.play(FadeIn(mitigation_group, shift=UP * 0.12))
        animated_top_icons = LaggedStart(
            Wiggle(nodes[0][1], scale_value=1.08, rotation_angle=0.04),
            Rotate(nodes[1][1][2], angle=TAU, about_point=nodes[1][1].get_center()),
            Indicate(nodes[2][1][2], scale_factor=1.18, color=PALETTE["resonance"]),
            Wiggle(nodes[3][1], scale_value=1.08, rotation_angle=0.035),
            Indicate(nodes[4][1][1], scale_factor=1.35, color=PALETTE["danger"]),
            lag_ratio=0.12,
        )
        animated_mitigations = LaggedStart(
            *[
                Indicate(item[0], scale_factor=1.12, color=PALETTE["electric"])
                for item in mitigation_items
            ],
            lag_ratio=0.08,
        )
        self.play(
            AnimationGroup(animated_top_icons, animated_mitigations, lag_ratio=0.0),
            run_time=3.2,
        )
        self.wait(0.8)
