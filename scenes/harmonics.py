from manim import *

from utils.plot_helpers import (
    PALETTE,
    configure_scene,
    make_component_label,
    make_note,
    make_title,
    make_wave_axes,
    waveform_component,
)


class FormaDeOndaHarmonica(Scene):
    def construct(self):
        configure_scene(self)

        title = make_title("How harmonics arise")
        equation = MathTex(
            r"i(t)=I_1\sin(\omega t)+I_3\sin(3\omega t+\phi_3)+I_5\sin(5\omega t+\phi_5)",
            font_size=34,
            color=PALETTE["text"],
        ).next_to(title, DOWN, buff=0.22)

        axes = make_wave_axes(x_length=10.7, y_length=4.1).shift(DOWN * 0.28)
        time_label = Text("time", font_size=20, color=PALETTE["muted"]).next_to(axes, DOWN, buff=0.18)
        current_label = Text("current", font_size=20, color=PALETTE["muted"]).rotate(PI / 2)
        current_label.next_to(axes, LEFT, buff=0.18)

        fundamental = axes.plot(waveform_component("fundamental"), x_range=[0, TAU, 0.02], color=PALETTE["electric"], stroke_width=4)
        third = axes.plot(waveform_component("third"), x_range=[0, TAU, 0.02], color=PALETTE["harmonic3"], stroke_width=4)
        fifth = axes.plot(waveform_component("fifth"), x_range=[0, TAU, 0.02], color=PALETTE["harmonic5"], stroke_width=4)
        summed = axes.plot(waveform_component("sum"), x_range=[0, TAU, 0.02], color=PALETTE["sum"], stroke_width=5)

        legend = VGroup(
            make_component_label("fundamental", PALETTE["electric"]),
            make_component_label("3rd harmonic", PALETTE["harmonic3"]),
            make_component_label("5th harmonic", PALETTE["harmonic5"]),
            make_component_label("sum", PALETTE["sum"]),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        legend.to_corner(DR, buff=0.55)

        note = make_note(
            "A distorted waveform can be decomposed into sinusoidal components.",
            font_size=24,
            color=PALETTE["text"],
        ).to_edge(DOWN, buff=0.28)

        self.play(Write(title), Write(equation))
        self.play(Create(axes), FadeIn(time_label), FadeIn(current_label))
        self.play(Create(fundamental), FadeIn(legend[0]))
        self.play(Create(third), FadeIn(legend[1]))
        self.play(Create(fifth), FadeIn(legend[2]))
        self.play(Create(summed), FadeIn(legend[3]), FadeIn(note, shift=UP * 0.15))
        self.wait(1.2)
