# ------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   big-vl
# Date:     November 30, 2022
#
# Description:  postprocessing-script Input shaping marlin, more: https://github.com/MarlinFirmware/Marlin/pull/24797
#
#
# ------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 9/01/2020
# ------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Application import Application
from UM.Logger import Logger

__version__ = "1.0"


class InputShaping(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Input Shaping",
            "key": "InputShaping",
            "metadata": {},
            "version": 2,
            "settings": {
                "setacceleration": {
                    "label": "Set Acceleration at step",
                    "description": "Set Acceleration at step, start: 2000",
                    "type": "int",
                    "default_value": 500
                },
                "zeta": {
                    "label": "Set Shaping Zeta Testing at step",
                    "description": "Set Input Shaping Zeta at step: start: 0.0",
                    "type": "float",
                    "default_value": 0.05,
                    "minimum_value": 0,
                    "maximum_value": 1,
                    "maximum_value_warning": 1
                },
                "jerk": {
                    "label": "E max jerk (units/s)",
                    "description": "E max jerk (units/s)",
                    "type": "float",
                    "default_value": 0.3,
                    "minimum_value": 0,
                    "maximum_value": 1.3,
                    "maximum_value_warning": 1.3
                },
                "changelayeroffset": {
                    "label": "Change Layer Offset",
                    "description": "If the print has a base, indicate the number of layers from which to start the changes.",
                    "type": "int",
                    "default_value": 50
                }
            }
        }"""

    def execute(self, data):
        setacceleration = int(self.getSettingValueByKey("setacceleration"))
        zeta = float(self.getSettingValueByKey("zeta"))
        changelayeroffset = int(self.getSettingValueByKey("changelayeroffset"))
        jerk = int(self.getSettingValueByKey("jerk"))
        _default_acceleration = 1500
        _curent_layer = 0
        _zeta = 0.10
        _step = 0
        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                line_index = lines.index(line)
                if line.startswith(";LAYER:"):
                    if _curent_layer == 0:
                        lines.insert(line_index + 1, "M205 J%s;" % (round(jerk, 2)))
                    if _curent_layer == _step:
                        if _default_acceleration < 7000:
                            lines.insert(
                                line_index + 1, "M204 P%s;" % (_default_acceleration)
                            )
                            _default_acceleration = (
                                _default_acceleration + setacceleration
                            )
                        if _zeta < 1:
                            lines.insert(
                                line_index + 2, "M593 D%s;" % (round(_zeta, 2))
                            )
                            _zeta += zeta
                        _step += changelayeroffset
                    _curent_layer += 1
            result = "\n".join(lines)
            data[layer_index] = result
        return data
