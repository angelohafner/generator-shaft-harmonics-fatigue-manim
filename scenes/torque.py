import numpy as np
from manim import *

from utils.electrical_shapes import make_flow_dots, make_generator, make_magnetic_field_lines
from utils.mechanical_shapes import make_cylindrical_shaft, make_torsion_wave, make_turbine
from utils.plot_helpers import PALETTE, configure_scene, make_note, make_title


def make_torque_indicator(
    center,
    radius: float,
    start_angle: float,
    angle: float,
    color,
) -> VGroup:
    """Create a partial torque arrow that stays outside the machine body."""
    end_angle = start_angle + angle
    arc = Arc(
        radius=radius,
        start_angle=start_angle,
        angle=angle,
        arc_center=center,
        color=color,
        stroke_width=4.4,
    )
    arc.set_fill(opacity=0)
    arc.set_stroke(color=color, width=4.4, opacity=0.88)
    tip_position = center + radius * np.array([np.cos(end_angle), np.sin(end_angle), 0.0])
    tangent_angle = end_angle + (PI / 2 if angle > 0 else -PI / 2)
    tip = Triangle(color=color, stroke_width=0)
    tip.set_fill(color, opacity=1.0)
    tip.set_height(0.17)
    tip.rotate(tangent_angle - PI / 2)
    tip.move_to(tip_position)
    return VGroup(arc, tip)


class TorqueEletromagnetico(Scene):
    def construct(self):
        configure_scene(self)

        title = make_title("From current to electromagnetic torque")
        power_eq = MathTex(r"T_e(t)=\frac{P_e(t)}{\omega_m}", font_size=38, color=PALETTE["text"])
        power_eq.next_to(title, DOWN, buff=0.25)

        note = make_note(
            "current with harmonics  ->  oscillating instantaneous power  ->  pulsating torque",
            font_size=24,
            color=PALETTE["muted"],
        ).next_to(power_eq, DOWN, buff=0.18)

        phase = ValueTracker(0.0)
        pulse = ValueTracker(0.0)
        left_center = LEFT * 3.75 + DOWN * 0.05
        right_center = RIGHT * 3.05 + DOWN * 0.05
        spring_center = (left_center + right_center) / 2

        turbine = make_turbine(radius=0.58, label="Turbine")
        turbine.shift(left_center - turbine[0].get_center())
        generator = make_generator(radius=0.66, label="Generator")
        generator.shift(right_center - generator[0].get_center())
        turbine[-1].shift(DOWN * 0.16)
        generator[-1].shift(DOWN * 0.16)
        turbine.set_z_index(4)
        generator.set_z_index(4)

        field = always_redraw(
            lambda: make_magnetic_field_lines(
                radius=0.76 + 0.035 * np.sin(phase.get_value()),
                count=4,
            )
            .move_to(right_center)
            .set_z_index(1)
        )

        shaft_start = left_center + RIGHT * 0.66
        shaft_end = right_center + LEFT * 0.76
        shaft = always_redraw(
            lambda: make_cylindrical_shaft(
                shaft_start,
                shaft_end,
                radius=0.145,
                twist=0.75 * np.sin(phase.get_value()),
                bands=9,
            ).set_z_index(2)
        )

        torsion_wave = always_redraw(
            lambda: make_torsion_wave(
                shaft_start,
                shaft_end,
                amplitude=0.13 + 0.04 * np.sin(phase.get_value()) ** 2,
                turns=6.0,
                phase=0.9 * phase.get_value(),
                color=PALETTE["mechanical"],
            )
            .set_z_index(5)
        )
        spring_label = MathTex(r"K", font_size=34, color=PALETTE["mechanical"]).next_to(spring_center, DOWN, buff=0.34)
        spring_note = VGroup(
            Text("torsional", font_size=18, color=PALETTE["muted"]),
            Text("stiffness", font_size=18, color=PALETTE["muted"]),
        ).arrange(RIGHT, buff=0.08).next_to(spring_label, DOWN, buff=0.04)

        tm_arrow = always_redraw(
            lambda: make_torque_indicator(
                left_center,
                radius=0.91 + 0.03 * np.sin(phase.get_value()) ** 2,
                start_angle=1.35 * PI,
                angle=-0.72 * PI,
                color=PALETTE["mechanical"],
            )
            .set_z_index(6)
        )
        te_arrow = always_redraw(
            lambda: make_torque_indicator(
                right_center,
                radius=0.94 + 0.04 * np.sin(phase.get_value()) ** 2,
                start_angle=-0.36 * PI,
                angle=0.72 * PI,
                color=PALETTE["electric"],
            )
            .set_z_index(6)
        )
        tm_label = MathTex(r"T_m", font_size=34, color=PALETTE["mechanical"])
        tm_label.move_to(left_center + LEFT * 1.02 + UP * 0.78)
        te_label = MathTex(r"T_e(t)", font_size=34, color=PALETTE["electric"])
        te_label.move_to(right_center + RIGHT * 1.05 + DOWN * 0.48)

        torque_pulse = always_redraw(
            lambda: VGroup(
                Circle(
                    radius=0.73 + 0.13 * np.sin(phase.get_value()) ** 2,
                    color=PALETTE["electric"],
                    stroke_width=2.5,
                ).move_to(right_center),
                Circle(
                    radius=0.9 + 0.12 * np.sin(phase.get_value() + PI / 3) ** 2,
                    color=PALETTE["electric"],
                    stroke_width=1.8,
                ).move_to(right_center),
            )
            .set_fill(opacity=0)
            .set_stroke(opacity=0.34)
            .set_z_index(0)
        )

        pulse_start = right_center + LEFT * 1.3 + UP * 0.86
        pulse_end = right_center + LEFT * 0.2 + UP * 0.86
        power_pulses = always_redraw(
            lambda: make_flow_dots(
                pulse_start,
                pulse_end,
                pulse.get_value(),
                PALETTE["electric"],
                count=5,
                radius=0.04 + 0.012 * np.sin(phase.get_value()) ** 2,
            ).set_z_index(5)
        )
        pulse_label = Text("power pulses", font_size=17, color=PALETTE["electric"]).next_to(
            Line(pulse_start, pulse_end), UP, buff=0.08
        )
        pulse_label.set_z_index(7)
        pulse_wire = Line(pulse_start, pulse_end, color=PALETTE["electric"], stroke_width=2.2).set_z_index(4)
        turbine_pulse_start = left_center + LEFT * 0.12 + UP * 0.92
        turbine_pulse_end = left_center + RIGHT * 1.08 + UP * 0.92
        turbine_power_pulses = always_redraw(
            lambda: make_flow_dots(
                turbine_pulse_start,
                turbine_pulse_end,
                pulse.get_value() + 0.35,
                PALETTE["mechanical"],
                count=5,
                radius=0.038 + 0.011 * np.sin(phase.get_value() + PI / 5) ** 2,
            ).set_z_index(5)
        )
        turbine_pulse_wire = Line(
            turbine_pulse_start,
            turbine_pulse_end,
            color=PALETTE["mechanical"],
            stroke_width=2.2,
        ).set_z_index(4)
        turbine_pulse_label = Text("power pulses", font_size=15, color=PALETTE["mechanical"]).next_to(
            turbine_pulse_wire, UP, buff=0.06
        )
        turbine_pulse_label.set_z_index(7)

        torque_state = Text("electric torque oscillates", font_size=17, color=PALETTE["electric"])
        torque_state.move_to(right_center + RIGHT * 1.85 + UP * 0.46)
        torque_state.set_z_index(7)

        spinning_parts = [
            (turbine[1], left_center, 1.8),
            (turbine[2], left_center, 1.8),
            (generator[1], right_center, 1.65),
            (generator[2], right_center, 1.65),
            (generator[3], right_center, 1.65),
        ]
        for part, center, speed in spinning_parts:
            part.add_updater(lambda mob, dt, c=center, s=speed: mob.rotate(s * dt, about_point=c))

        simple_eq = MathTex(
            r"J\frac{d^2\theta}{dt^2}=T_m-T_e(t)",
            font_size=36,
            color=PALETTE["text"],
        ).to_edge(DOWN, buff=0.9)
        full_eq = MathTex(
            r"J\frac{d^2\theta}{dt^2}+D\frac{d\theta}{dt}+K\theta=T_m-T_e(t)",
            font_size=34,
            color=PALETTE["text"],
        ).to_edge(DOWN, buff=0.9)

        def make_variable_definition(symbol: str, description: str) -> VGroup:
            """Create a compact definition with the variable rendered by LaTeX."""
            variable = MathTex(symbol, font_size=23, color=PALETTE["text"])
            meaning = Text(f": {description}", font_size=19, color=PALETTE["muted"])
            return VGroup(variable, meaning).arrange(RIGHT, buff=0.04)

        variable_note = VGroup(
            make_variable_definition(r"J", "inertia"),
            make_variable_definition(r"D", "damping"),
            make_variable_definition(r"K", "stiffness"),
            make_variable_definition(r"\theta", "twist angle"),
        ).arrange(RIGHT, buff=0.26)
        if variable_note.width > 11.6:
            variable_note.scale_to_fit_width(11.6)
        variable_note.next_to(full_eq, DOWN, buff=0.18)

        self.play(Write(title), Write(power_eq), FadeIn(note, shift=DOWN * 0.1))
        self.play(
            FadeIn(turbine),
            FadeIn(shaft),
            Create(torsion_wave),
            FadeIn(spring_label),
            FadeIn(spring_note),
            FadeIn(field),
            FadeIn(torque_pulse),
            FadeIn(generator),
            phase.animate.set_value(1.6 * PI),
            run_time=2.2,
            rate_func=linear,
        )
        self.play(
            FadeIn(tm_arrow),
            FadeIn(te_arrow),
            FadeIn(tm_label),
            FadeIn(te_label),
            Create(turbine_pulse_wire),
            FadeIn(turbine_power_pulses),
            FadeIn(turbine_pulse_label),
            Create(pulse_wire),
            FadeIn(power_pulses),
            FadeIn(pulse_label),
            Write(simple_eq),
            phase.animate.set_value(3.2 * PI),
            pulse.animate.set_value(1.4),
            run_time=2.2,
            rate_func=linear,
        )
        self.play(
            FadeIn(torque_state),
            phase.animate.set_value(7.0 * PI),
            pulse.animate.set_value(4.2),
            run_time=3.6,
            rate_func=linear,
        )
        self.play(
            ReplacementTransform(simple_eq, full_eq),
            FadeIn(variable_note, shift=UP * 0.1),
            phase.animate.set_value(8.2 * PI),
            pulse.animate.set_value(5.0),
            run_time=1.4,
            rate_func=linear,
        )
        self.play(
            phase.animate.set_value(12.0 * PI),
            pulse.animate.set_value(8.0),
            run_time=3.4,
            rate_func=linear,
        )
        self.wait(0.6)

        for part, _, _ in spinning_parts:
            part.clear_updaters()
