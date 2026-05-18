from scenes.fatigue import Conclusao as _Conclusao
from scenes.fatigue import FadigaEixoGerador as _FadigaEixoGerador
from scenes.harmonics import FormaDeOndaHarmonica as _FormaDeOndaHarmonica
from scenes.intro import IntroducaoHarmonicos as _IntroducaoHarmonicos
from scenes.shaft_model import FrequenciaTorque as _FrequenciaTorque
from scenes.shaft_model import ModeloTorcional as _ModeloTorcional
from scenes.torque import TorqueEletromagnetico as _TorqueEletromagnetico


class IntroducaoHarmonicos(_IntroducaoHarmonicos):
    pass


class FormaDeOndaHarmonica(_FormaDeOndaHarmonica):
    pass


class TorqueEletromagnetico(_TorqueEletromagnetico):
    pass


class ModeloTorcional(_ModeloTorcional):
    pass


class FrequenciaTorque(_FrequenciaTorque):
    pass


class FadigaEixoGerador(_FadigaEixoGerador):
    pass


class Conclusao(_Conclusao):
    pass


__all__ = [
    "IntroducaoHarmonicos",
    "FormaDeOndaHarmonica",
    "TorqueEletromagnetico",
    "ModeloTorcional",
    "FrequenciaTorque",
    "FadigaEixoGerador",
    "Conclusao",
]
