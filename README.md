# Electrical harmonics and torsional fatigue in generator shafts

Educational Python project using Manim Community Edition to explain, visually, how harmonic currents can create pulsating electromagnetic torque, excite torsional vibrations, and contribute to mechanical fatigue in shafts of large synchronous generators.

The project does not use external images. All drawings are vector objects created with Manim.

## Requirements

- Python 3.10 or newer.
- FFmpeg available on the `PATH`.
- A LaTeX distribution for rendering `MathTex`, such as MiKTeX or TeX Live.
- Manim Community Edition, installed from this project's dependencies.

## Installation

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Rendering

Fast low-quality render:

```bash
manim -pql main.py IntroducaoHarmonicos
manim -pql main.py TorqueEletromagnetico
manim -pql main.py ModeloTorcional
manim -pql main.py FrequenciaTorque
manim -pql main.py FadigaEixoGerador
manim -pql main.py Conclusao
```

To render without opening the video player, remove `-p`:

```bash
manim -ql main.py IntroducaoHarmonicos
```

For higher quality, use `-pqm` or `-pqh` instead of `-pql`.

## Suggested teaching sequence

1. `IntroducaoHarmonicos` introduces the overall causal chain.
2. `TorqueEletromagnetico` connects instantaneous power, torque, and angular dynamics.
3. `ModeloTorcional` represents the turbine-generator shaft as a mass-spring system.
4. `FrequenciaTorque` shows why risk depends on the match between pulsating torque and torsional modes.
5. `FadigaEixoGerador` shows stress cycles, the S-N curve, and Miner's accumulated damage rule.
6. `Conclusao` summarizes the technical cautions and mitigation measures.

## Core technical message

The project avoids the simplistic claim that any harmonic breaks a shaft. Risk depends on harmonic amplitude, torque oscillation frequencies, natural torsional frequencies of the turbine-generator train, damping, exposure duration, and accumulated fatigue damage.

## Structure

```text
main.py
README.md
requirements.txt
scenes/
  intro.py
  harmonics.py
  torque.py
  shaft_model.py
  fatigue.py
utils/
  electrical_shapes.py
  mechanical_shapes.py
  plot_helpers.py
```
