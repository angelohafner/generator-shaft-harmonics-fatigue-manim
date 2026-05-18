from manim import *

from utils.electrical_shapes import (
    make_current_arrow,
    make_flow_dots,
    make_generator,
    make_load,
    make_magnetic_field_lines,
)
from utils.mechanical_shapes import make_cylindrical_shaft, make_torque_arrow, make_turbine
from utils.plot_helpers import (
    PALETTE,
    configure_scene,
    make_component_label,
    make_note,
    make_title,
    make_wave_axes,
    waveform_component,
)


class IntroducaoHarmonicos(Scene):
    def construct(self):
        configure_scene(self)

        title = make_title("Electrical harmonics and torsional fatigue")
        question = make_note(
            "Can electrical harmonics fatigue a generator shaft?",
            font_size=28,
            color=PALETTE["text"],
        ).next_to(title, DOWN, buff=0.22)

        phase = ValueTracker(0.0)
        flow_phase = ValueTracker(0.0)
        harmonic_pulse = ValueTracker(0.0)

        turbine_center = LEFT * 4.55 + UP * 0.95
        generator_center = LEFT * 1.35 + UP * 0.95
        load_center = RIGHT * 3.65 + UP * 0.95

        turbine = make_turbine(radius=0.66)
        turbine.shift(turbine_center - turbine[0].get_center())
        generator = make_generator(radius=0.7)
        generator.shift(generator_center - generator[0].get_center())
        load = make_load(width=1.62, height=1.08)
        load.shift(load_center - load[0].get_center())
        turbine[-1].shift(DOWN * 0.18)
        generator[-1].shift(DOWN * 0.18)
        turbine.set_z_index(3)
        generator.set_z_index(3)
        load.set_z_index(3)

        shaft_start = turbine_center + RIGHT * 0.68
        shaft_end = generator_center + LEFT * 0.76
        shaft = always_redraw(
            lambda: make_cylindrical_shaft(
                shaft_start
                + harmonic_pulse.get_value()
                * (
                    UP * 0.035 * np.sin(9.0 * phase.get_value())
                    + RIGHT * 0.012 * np.sin(13.0 * phase.get_value())
                ),
                shaft_end
                + harmonic_pulse.get_value()
                * (
                    UP * 0.035 * np.sin(9.0 * phase.get_value())
                    + RIGHT * 0.012 * np.sin(13.0 * phase.get_value())
                ),
                radius=0.15,
                twist=(
                    0.48
                    + 0.18 * harmonic_pulse.get_value() * np.sin(5.0 * phase.get_value()) ** 2
                )
                * np.sin(phase.get_value()),
                bands=6,
            ).set_z_index(2)
        )

        top_wire_start = generator_center + RIGHT * 0.78 + UP * 0.18
        top_wire_end = load_center + LEFT * 0.98 + UP * 0.18
        bottom_wire_start = generator_center + RIGHT * 0.78 + DOWN * 0.18
        bottom_wire_end = load_center + LEFT * 0.98 + DOWN * 0.18
        wires = VGroup(
            Line(top_wire_start, top_wire_end, color=PALETTE["electric"], stroke_width=3.2),
            Line(bottom_wire_start, bottom_wire_end, color=PALETTE["electric"], stroke_width=3.2),
        )
        wires.set_z_index(1)

        ideal_flow = always_redraw(
            lambda: VGroup(
                make_flow_dots(
                    top_wire_start,
                    top_wire_end,
                    flow_phase.get_value(),
                    PALETTE["electric"],
                    count=7,
                ),
                make_flow_dots(
                    bottom_wire_start,
                    bottom_wire_end,
                    flow_phase.get_value() + 0.08,
                    PALETTE["electric"],
                    count=7,
                    reverse=True,
                ),
            )
        )
        distorted_flow = always_redraw(
            lambda: VGroup(
                make_flow_dots(
                    top_wire_end,
                    top_wire_start,
                    1.45 * flow_phase.get_value(),
                    PALETTE["harmonic3"],
                    count=9,
                    radius=0.04,
                ),
                make_flow_dots(
                    bottom_wire_start,
                    bottom_wire_end,
                    1.45 * flow_phase.get_value() + 0.14,
                    PALETTE["sum"],
                    count=6,
                    radius=0.036,
                ),
            )
        )
        ideal_flow.set_z_index(2)
        distorted_flow.set_z_index(2)

        ideal_arrow = make_current_arrow(
            top_wire_start + DOWN * 0.62,
            top_wire_end + DOWN * 0.62,
            "sinusoidal current",
            PALETTE["electric"],
        )
        ideal_arrow[1].next_to(ideal_arrow[0], DOWN, buff=0.08)
        ideal_arrow.set_z_index(4)
        distorted_arrow = make_current_arrow(
            bottom_wire_end + DOWN * 0.55,
            bottom_wire_start + DOWN * 0.55,
            "distorted current",
            PALETTE["harmonic3"],
        )
        distorted_arrow[1].next_to(distorted_arrow[0], DOWN, buff=0.08)
        distorted_arrow.set_z_index(4)

        turbine_motion = always_redraw(
            lambda: make_torque_arrow(
                turbine_center,
                radius=0.9
                + 0.07 * harmonic_pulse.get_value() * np.sin(5.0 * phase.get_value()) ** 2,
                color=PALETTE["mechanical"],
                clockwise=False,
            )
            .rotate(
                0.35 * phase.get_value()
                + 0.11 * harmonic_pulse.get_value() * np.sin(5.0 * phase.get_value()),
                about_point=turbine_center,
            )
            .set_opacity(0.62 + 0.16 * harmonic_pulse.get_value() * np.sin(5.0 * phase.get_value()) ** 2)
            .set_z_index(2)
        )
        generator_motion = always_redraw(
            lambda: make_torque_arrow(
                generator_center,
                radius=0.9
                + 0.08 * harmonic_pulse.get_value() * np.sin(5.5 * phase.get_value()) ** 2,
                color=PALETTE["electric"],
                clockwise=False,
            )
            .rotate(
                0.35 * phase.get_value()
                + 0.13 * harmonic_pulse.get_value() * np.sin(5.5 * phase.get_value()),
                about_point=generator_center,
            )
            .set_opacity(0.58 + 0.18 * harmonic_pulse.get_value() * np.sin(5.5 * phase.get_value()) ** 2)
            .set_z_index(2)
        )
        field = always_redraw(
            lambda: make_magnetic_field_lines(
                radius=0.78
                + 0.02 * np.sin(phase.get_value())
                + 0.04 * harmonic_pulse.get_value() * np.sin(6.0 * phase.get_value()) ** 2,
                count=4,
            )
            .move_to(generator_center)
            .set_z_index(0)
        )

        spinning_parts = [
            (turbine[1], turbine_center, 1.65),
            (turbine[2], turbine_center, 1.65),
            (generator[1], generator_center, 1.65),
            (generator[2], generator_center, 1.65),
            (generator[3], generator_center, 1.65),
        ]
        for part, center, speed in spinning_parts:
            part.add_updater(
                lambda mob, dt, c=center, s=speed: mob.rotate(
                    s
                    * (
                        1.0
                        + harmonic_pulse.get_value()
                        * (
                            0.22 * np.sin(5.0 * phase.get_value())
                            + 0.08 * np.sin(11.0 * phase.get_value())
                        )
                    )
                    * dt,
                    about_point=c,
                )
            )

        axes = make_wave_axes(x_length=5.2, y_length=1.65).move_to(DOWN * 1.75 + LEFT * 3.0)
        sine = axes.plot(
            waveform_component("fundamental"),
            x_range=[0, TAU, 0.03],
            color=PALETTE["electric"],
            stroke_width=4,
        )
        distorted = axes.plot(
            waveform_component("sum"),
            x_range=[0, TAU, 0.03],
            color=PALETTE["sum"],
            stroke_width=4,
        )
        sine_label = make_component_label("sinusoidal", PALETTE["electric"], 19).next_to(axes, DOWN, buff=0.18)
        distorted_label = make_component_label("with harmonics", PALETTE["sum"], 19).next_to(axes, DOWN, buff=0.18)

        causal_terms = [
            ("Harmonics", PALETTE["harmonic3"]),
            ("Pulsating torque", PALETTE["electric"]),
            ("Torsional vibration", PALETTE["mechanical"]),
            ("Fatigue", PALETTE["fatigue"]),
        ]
        causal = VGroup()
        for index, (text, color) in enumerate(causal_terms):
            item = Text(text, font_size=23, color=color)
            causal.add(item)
            if index < len(causal_terms) - 1:
                causal.add(Arrow(LEFT * 0.25, RIGHT * 0.25, buff=0.08, color=PALETTE["muted"], stroke_width=3))
        causal.arrange(RIGHT, buff=0.22).to_edge(DOWN, buff=0.45)

        self.play(
            Write(title),
            FadeIn(question, shift=DOWN * 0.15),
            phase.animate.set_value(0.8 * PI),
            flow_phase.animate.set_value(0.45),
            run_time=1.5,
        )
        self.play(
            FadeIn(turbine),
            FadeIn(shaft),
            FadeIn(turbine_motion),
            FadeIn(generator),
            FadeIn(field),
            FadeIn(generator_motion),
            Create(wires),
            FadeIn(load),
            FadeIn(ideal_flow),
            phase.animate.set_value(2.2 * PI),
            flow_phase.animate.set_value(1.4),
            run_time=2.2,
            rate_func=linear,
        )
        self.play(
            FadeIn(ideal_arrow),
            Create(axes),
            Create(sine),
            FadeIn(sine_label),
            phase.animate.set_value(3.2 * PI),
            flow_phase.animate.set_value(2.15),
            run_time=1.7,
            rate_func=linear,
        )
        self.play(
            phase.animate.set_value(4.3 * PI),
            flow_phase.animate.set_value(3.0),
            run_time=1.0,
            rate_func=linear,
        )
        self.play(
            ReplacementTransform(ideal_arrow, distorted_arrow),
            FadeOut(ideal_flow),
            FadeIn(distorted_flow),
            Transform(sine, distorted),
            ReplacementTransform(sine_label, distorted_label),
            phase.animate.set_value(5.8 * PI),
            flow_phase.animate.set_value(4.2),
            harmonic_pulse.animate.set_value(1.0),
            run_time=2.0,
            rate_func=linear,
        )
        self.play(
            LaggedStart(*[FadeIn(mob, shift=UP * 0.12) for mob in causal], lag_ratio=0.12),
            phase.animate.set_value(7.0 * PI),
            flow_phase.animate.set_value(5.0),
            run_time=1.8,
            rate_func=linear,
        )
        self.play(
            phase.animate.set_value(8.3 * PI),
            flow_phase.animate.set_value(6.0),
            run_time=1.3,
            rate_func=linear,
        )

        for part, _, _ in spinning_parts:
            part.clear_updaters()
