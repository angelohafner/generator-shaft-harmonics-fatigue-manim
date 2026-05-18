import numpy as np
from manim import *

from utils.mechanical_shapes import make_cylindrical_shaft, make_torsion_wave, make_torsional_spring
from utils.plot_helpers import PALETTE, configure_scene, make_note, make_resonance_plot, make_title


def make_pointer_disc(
    radius: float,
    label: str,
    angle: float,
    amplitude: float,
    color: str,
) -> VGroup:
    """Create a torsional inertia disk with a clear pointer and motion range."""
    active_color = PALETTE["danger"] if amplitude > 0.95 else color
    disk = Circle(radius=radius, color=PALETTE["shaft"], stroke_width=4)
    disk.set_fill(PALETTE["panel"], opacity=1.0)
    inner = Circle(radius=radius * 0.72, color=active_color, stroke_width=1.5)
    inner.set_opacity(0.6 if amplitude > 0.95 else 0.45)
    hub = Dot(ORIGIN, radius=radius * 0.08, color=active_color)

    ticks = VGroup()
    for index in range(12):
        tick_angle = index * TAU / 12
        start = radius * 0.82 * np.array([np.cos(tick_angle), np.sin(tick_angle), 0])
        end = radius * 0.94 * np.array([np.cos(tick_angle), np.sin(tick_angle), 0])
        tick = Line(start, end, color=PALETTE["muted"], stroke_width=1.2)
        tick.set_opacity(0.55)
        ticks.add(tick)

    pointer_end = radius * 0.82 * np.array([np.cos(angle), np.sin(angle), 0])
    pointer = Line(ORIGIN, pointer_end, color=active_color, stroke_width=6 if amplitude > 0.95 else 5)
    tip = Dot(pointer_end, radius=radius * (0.072 if amplitude > 0.95 else 0.055), color=active_color)

    sweep = VGroup()
    if amplitude > 0.55:
        sweep_angle = min(2 * amplitude, 1.82 * PI)
        sweep = Arc(
            radius=radius * 1.14,
            start_angle=-sweep_angle / 2,
            angle=sweep_angle,
            color=PALETTE["danger"] if amplitude > 0.95 else PALETTE["resonance"],
            stroke_width=5 if amplitude > 0.95 else 3.5,
        )
        sweep.set_opacity(0.82 if amplitude > 0.95 else 0.55)

    ghosts = VGroup()
    if amplitude > 0.95:
        for ghost_angle in [-amplitude, -0.5 * amplitude, 0.5 * amplitude, amplitude]:
            end = radius * 0.72 * np.array([np.cos(ghost_angle), np.sin(ghost_angle), 0])
            ghost = Line(ORIGIN, end, color=PALETTE["danger"], stroke_width=2.4)
            ghost.set_opacity(0.34)
            ghosts.add(ghost)

    text = Text(label, font_size=20, color=PALETTE["text"]).next_to(disk, DOWN, buff=0.16)
    return VGroup(sweep, disk, inner, ticks, ghosts, pointer, tip, hub, text)


def place_pointer_disc_at_center(disc: VGroup, center: np.ndarray) -> VGroup:
    """Place a labeled pointer disk by the physical disk center."""
    disc.shift(center - disc[1].get_center())
    return disc


class ModeloTorcional(Scene):
    def construct(self):
        configure_scene(self)

        title = make_title("Torsional mass-spring model")
        omega_eq = MathTex(r"\omega_n=\sqrt{\frac{K}{J_{eq}}}", font_size=36, color=PALETTE["text"])
        resonance_eq = MathTex(r"f_{torque}\approx f_n", font_size=38, color=PALETTE["resonance"])
        equations = VGroup(omega_eq, resonance_eq).arrange(RIGHT, buff=1.4).next_to(title, DOWN, buff=0.18)

        phase = ValueTracker(0.0)
        amplitude = ValueTracker(0.18)
        frequency = ValueTracker(0.35)
        left_center = LEFT * 4.25 + UP * 0.25
        right_center = LEFT * 2.15 + UP * 0.25
        model_mid = (left_center + right_center) / 2

        left_disc = always_redraw(
            lambda: place_pointer_disc_at_center(
                make_pointer_disc(
                    radius=0.53,
                    label="turbine",
                    angle=amplitude.get_value() * np.sin(phase.get_value()),
                    amplitude=amplitude.get_value(),
                    color=PALETTE["mechanical"],
                ),
                left_center,
            )
        )
        right_disc = always_redraw(
            lambda: place_pointer_disc_at_center(
                make_pointer_disc(
                    radius=0.53,
                    label="rotor",
                    angle=-amplitude.get_value() * np.sin(phase.get_value()),
                    amplitude=amplitude.get_value(),
                    color=PALETTE["mechanical"],
                ),
                right_center,
            )
        )
        spring = always_redraw(
            lambda: make_torsional_spring(
                length=0.9 + 0.08 * np.sin(phase.get_value()),
                amplitude=0.11 + 0.035 * min(amplitude.get_value(), 1.15),
                turns=5,
            ).move_to(model_mid + UP * 0.01)
        )
        k_label = MathTex(r"K", color=PALETTE["mechanical"], font_size=34).next_to(model_mid, DOWN, buff=0.34)
        model_label = VGroup(
            Text("two inertias", font_size=18, color=PALETTE["muted"]),
            MathTex("+", font_size=22, color=PALETTE["muted"]),
            Text("stiffness", font_size=18, color=PALETTE["muted"]),
            MathTex("K", font_size=22, color=PALETTE["mechanical"]),
        ).arrange(RIGHT, buff=0.1)
        model_label.move_to(model_mid + DOWN * 1.38)

        axes, curve, labels = make_resonance_plot(width=4.25, height=2.55)
        plot = VGroup(axes, curve, labels).move_to(RIGHT * 2.85 + DOWN * 0.28)
        resonance_band = Rectangle(
            width=0.38,
            height=2.55,
            stroke_width=0,
            fill_color=PALETTE["danger"],
            fill_opacity=0.18,
        ).move_to(axes.c2p(1.0, 3.25))
        resonance_band.set_z_index(-1)
        moving_line = always_redraw(
            lambda: DashedLine(
                axes.c2p(frequency.get_value(), 0),
                axes.c2p(frequency.get_value(), 6.55),
                color=PALETTE["electric"],
                stroke_width=3,
            )
        )
        moving_dot = always_redraw(
            lambda: Dot(
                axes.c2p(
                    frequency.get_value(),
                    min(
                        6.8,
                        1.0
                        / np.sqrt(
                            (1 - frequency.get_value() ** 2) ** 2
                            + (0.16 * frequency.get_value()) ** 2
                        ),
                    ),
                ),
                color=PALETTE["electric"],
            )
        )

        state_label = Text("slow excitation: pointers almost still", font_size=23, color=PALETTE["electric"])
        state_label.to_edge(DOWN, buff=0.45)
        warning = always_redraw(
            lambda: Text(
                "RESONANCE",
                font_size=30 + 4 * np.sin(phase.get_value()) ** 2,
                color=PALETTE["danger"],
            )
            .next_to(model_mid, UP, buff=1.05)
            .set_opacity(1.0 if amplitude.get_value() > 0.95 else 0.0)
        )
        amplification_arrow = always_redraw(
            lambda: Arrow(
                model_mid + DOWN * 0.95,
                model_mid + UP * (0.72 + 0.2 * np.sin(phase.get_value()) ** 2),
                color=PALETTE["danger"],
                stroke_width=5,
                max_tip_length_to_length_ratio=0.16,
            ).set_opacity(1.0 if amplitude.get_value() > 0.95 else 0.0)
        )

        self.play(Write(title), Write(equations))
        self.play(FadeIn(left_disc), FadeIn(right_disc), Create(spring), FadeIn(k_label), FadeIn(model_label))
        self.play(
            FadeIn(resonance_band),
            Create(axes),
            Create(curve),
            FadeIn(labels),
            FadeIn(moving_line),
            FadeIn(moving_dot),
            FadeIn(state_label),
        )
        self.add(warning, amplification_arrow)
        self.play(phase.animate.set_value(2.5 * PI), run_time=2.6, rate_func=linear)
        self.play(
            frequency.animate.set_value(1.55),
            amplitude.animate.set_value(0.38),
            Transform(
                state_label,
                Text("away from resonance: moderate oscillation", font_size=23, color=PALETTE["electric"]).to_edge(DOWN, buff=0.45),
            ),
            run_time=1.3,
        )
        self.play(phase.animate.set_value(6.2 * PI), run_time=3.0, rate_func=linear)
        self.play(
            frequency.animate.set_value(1.0),
            amplitude.animate.set_value(2.25),
            Transform(
                state_label,
                Text("resonance: small excitation, large twist", font_size=24, color=PALETTE["danger"]).to_edge(DOWN, buff=0.45),
            ),
            run_time=1.8,
        )
        self.play(phase.animate.set_value(14.5 * PI), run_time=6.0, rate_func=linear)
        self.wait(1.0)


class FrequenciaTorque(Scene):
    def construct(self):
        configure_scene(self)

        title = make_title("Electrical harmonic and torque frequency")
        note = make_note(
            "The link between harmonic order and torque depends on sequence, machine, and grid.",
            font_size=23,
            color=PALETTE["muted"],
        ).next_to(title, DOWN, buff=0.18)

        phase = ValueTracker(0.0)

        shaft_start = LEFT * 6.72 + DOWN * 1.54
        shaft_end = RIGHT * 6.72 + DOWN * 1.54
        shaft_center = (shaft_start + shaft_end) / 2
        shaft = always_redraw(
            lambda: make_cylindrical_shaft(
                shaft_start,
                shaft_end,
                radius=0.28,
                twist=0.78 * np.sin(phase.get_value()),
                bands=16,
            ).set_z_index(2)
        )
        torsion_wave = always_redraw(
            lambda: make_torsion_wave(
                shaft_start,
                shaft_end,
                amplitude=0.19 + 0.06 * np.sin(phase.get_value()) ** 2,
                turns=5.2,
                phase=1.15 * phase.get_value(),
                color=PALETTE["resonance"],
            ).set_z_index(5)
        )
        mode_arc = Arc(
            radius=2.15,
            start_angle=PI * 0.18,
            angle=PI * 0.64,
            color=PALETTE["resonance"],
            stroke_width=5.2,
        )
        mode_arc.move_to(shaft_center + UP * 0.52)
        mode_label = MathTex(r"f_n", color=PALETTE["resonance"], font_size=46)
        mode_label.move_to(shaft_center + RIGHT * 1.82 + UP * 1.32)

        spectrum_y = 0.58
        spectrum_left = np.array([-5.85, spectrum_y, 0.0])
        spectrum_right = np.array([5.85, spectrum_y, 0.0])
        spectrum_axis = Arrow(
            spectrum_left,
            spectrum_right,
            buff=0.0,
            color=PALETTE["muted"],
            stroke_width=3.1,
            max_tip_length_to_length_ratio=0.05,
        )
        spectrum_title = Text("torque components", font_size=27, color=PALETTE["text"])
        spectrum_title.move_to(spectrum_left + RIGHT * 1.95 + UP * 0.86)
        spectrum_axis_label = MathTex(r"f", font_size=36, color=PALETTE["muted"]).next_to(spectrum_axis, RIGHT, buff=0.1)

        selected_x = shaft_center[0]
        components = [
            (-5.35, 0.54, r"f_1", PALETTE["electric"], False),
            (-3.65, 0.72, r"f_2", PALETTE["electric"], False),
            (selected_x, 1.72, r"f_{torque}", PALETTE["resonance"], True),
            (3.95, 0.58, r"f_3", PALETTE["electric"], False),
        ]

        spectrum_components = VGroup()
        for x_pos, height, label_text, color, selected in components:
            base = np.array([x_pos, spectrum_y, 0.0])
            top = base + UP * height
            stem = Line(base, top, color=color, stroke_width=6.2 if selected else 4.2)
            dot = Dot(top, radius=0.075 if selected else 0.052, color=color)
            label = MathTex(label_text, font_size=34 if selected else 26, color=color)
            if selected:
                label.move_to(base + LEFT * 0.54 + DOWN * 0.34)
            else:
                label.next_to(base, DOWN, buff=0.11)
            spectrum_components.add(VGroup(stem, dot, label))

        excitation_arrow = always_redraw(
            lambda: Arrow(
                np.array([selected_x, spectrum_y - 0.14, 0.0]),
                shaft_center + UP * (0.57 + 0.05 * np.sin(phase.get_value()) ** 2),
                buff=0.03,
                color=PALETTE["resonance"],
                stroke_width=5.2,
                max_tip_length_to_length_ratio=0.16,
            ).set_z_index(7)
        )
        excitation_dot = always_redraw(
            lambda: Dot(
                interpolate(
                    np.array([selected_x, spectrum_y - 0.23, 0.0]),
                    shaft_center + UP * 0.62,
                    (0.5 + 0.5 * np.sin(phase.get_value())) ** 1.4,
                ),
                radius=0.058,
                color=PALETTE["resonance"],
            ).set_z_index(8)
        )
        spectrum = VGroup(spectrum_axis, spectrum_title, spectrum_axis_label, spectrum_components)

        highlight = MathTex(
            r"f_{torque}\approx f_n",
            color=PALETTE["resonance"],
            font_size=50,
        ).move_to(shaft_center + DOWN * 1.15)
        risk = make_note(
            "Risk increases when a torque component coincides with a torsional mode.",
            font_size=26,
            color=PALETTE["text"],
        ).to_edge(DOWN, buff=0.32)

        self.play(Write(title), FadeIn(note, shift=DOWN * 0.1))
        self.play(FadeIn(shaft), Create(torsion_wave), Create(mode_arc), FadeIn(mode_label))
        self.play(Create(spectrum_axis), FadeIn(spectrum_title), FadeIn(spectrum_axis_label))
        self.play(
            LaggedStart(*[FadeIn(component, shift=UP * 0.08) for component in spectrum_components], lag_ratio=0.12),
        )
        self.play(FadeIn(excitation_arrow), FadeIn(excitation_dot))
        self.play(
            Write(highlight),
            FadeIn(risk, shift=UP * 0.12),
            phase.animate.set_value(2.8 * PI),
            run_time=2.2,
            rate_func=linear,
        )
        self.play(phase.animate.set_value(7.2 * PI), run_time=3.2, rate_func=linear)
        self.wait(0.6)
