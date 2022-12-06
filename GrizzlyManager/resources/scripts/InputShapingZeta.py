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


class InputShapingZeta(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Input Shaping Zeta",
            "key": "InputShapingZeta",
            "metadata": {},
            "version": 2,
            "settings": {
                "setacceleration": {
                    "label": "Set Acceleration",
                    "description": "Set Acceleration",
                    "type": "int",
                    "default_value": 500,
                    "maximum_value_warning": 7000
                },
                "ratio_options": {
                    "label": "Damping ratio (Zeta) at",
                    "description": "Damping ratio (Zeta) at",
                    "type": "enum",
                    "options": {
                        "ALL": "All",
                        "Y": "Y",
                        "X": "X"
                    },
                    "default_value": "ALL"
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
                "step_height": {
                    "label": "Step height",
                    "description": "Step height",
                    "type": "int",
                    "default_value": 50
                }
            }
        }"""

    def _set_damping_ratio(self, ratio_options, list_, index_, val):
        if val == 0:
            val = 0.01
        if val >= 0.01 and val <= 1:
            if ratio_options == "ALL":
                list_.insert(
                    index_, "M593 D%s" % (val)
                )
            if ratio_options == "X":
                list_.insert(
                    index_, "M593 D%s X" % (val)
                )
            if ratio_options == "Y":
                list_.insert(
                    index_, "M593 D%s Y" % (val)
                )

    def execute(self, data):
        setacceleration = int(self.getSettingValueByKey("setacceleration"))
        ratio_options = self.getSettingValueByKey("ratio_options")
        zeta = round(float(self.getSettingValueByKey("zeta")), 2)
        step_height = int(self.getSettingValueByKey("step_height"))
        _curent_layer = 0
        _zeta = 0.00
        _step = 0
        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                line_index = lines.index(line)
                if line.startswith(";LAYER:"):
                    if _curent_layer == 0:
                        if setacceleration > 0 and setacceleration < 7000:
                            lines.insert(
                                line_index, "M204 S%s" % (setacceleration)
                            )
                            lines.insert(
                                line_index + 1, "M204 P%s" % (setacceleration)
                            )
                    if _curent_layer == _step:
                        _zeta = round(_zeta, 2)
                        self._set_damping_ratio(ratio_options, lines, line_index, _zeta)
                        _zeta += zeta
                        _step += step_height
                    _curent_layer += 1
            result = "\n".join(lines)
            data[layer_index] = result
        return data
