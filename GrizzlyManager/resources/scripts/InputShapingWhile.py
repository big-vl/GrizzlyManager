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


class InputShapingWhile(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Input Shaping While",
            "key": "InputShapingWhile",
            "metadata": {},
            "version": 2,
            "settings": {
                "setacceleration": {
                    "label": "Set Acceleration",
                    "description": "Set Acceleration",
                    "type": "int",
                    "default_value": 3000
                },
                "set_damping_ratio": {
                    "label": "Set damping ration (Zeta)",
                    "description": "Set damping ration (Zeta) 0.00 - Off",
                    "type": "float",
                    "default_value": 0.30,
                    "minimum_value": 0.00,
                    "maximum_value": 1
                },
                "freq_options": {
                    "label": "Freq at",
                    "description": "Freq at",
                    "type": "enum",
                    "options": {
                        "ALL": "All",
                        "Y": "Y",
                        "X": "X"
                    },
                    "default_value": "ALL"
                },
                "startfreq": {
                    "label": "Start Freq",
                    "description": "Start Freq",
                    "type": "float",
                    "default_value": 0,
                    "minimum_value": 0,
                    "maximum_value": 200
                },
                "step_delta_freq": {
                    "label": "Step delta freq",
                    "description": "Step delta freq",
                    "type": "float",
                    "default_value": 5
                },
                "step_height": {
                    "label": "Step height",
                    "description": "Step height",
                    "type": "int",
                    "default_value": 25
                }
            }
        }"""

    def _set_freq(self, freq_options, list_, index_, val):
        if val == 0:
            val = 1
        if val >= 1 and val <= 200:
            if freq_options == "ALL":
                list_.insert(
                    index_, "M593 F%s" % (val)
                )
            if freq_options == "X":
                list_.insert(
                    index_, "M593 F%s X" % (val)
                )
            if freq_options == "Y":
                list_.insert(
                    index_, "M593 F%s Y" % (val)
                )

    def execute(self, data):
        setacceleration = int(self.getSettingValueByKey("setacceleration"))
        freq_options = self.getSettingValueByKey("freq_options")
        set_damping_ratio = round(float(self.getSettingValueByKey("set_damping_ratio")), 2)
        startfreq = round(float(self.getSettingValueByKey("startfreq")), 2)
        step_delta_freq = round(float(self.getSettingValueByKey("step_delta_freq")), 2)
        step_height = int(self.getSettingValueByKey("step_height"))
        _curent_layer = 0
        _step_height = 0
        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                line_index = lines.index(line)
                if line.startswith(";LAYER:"):
                    if _curent_layer == 0:
                        lines.insert(
                            line_index, "M204 S%s" % (setacceleration)
                        )
                        lines.insert(
                            line_index + 1, "M204 P%s" % (setacceleration)
                        )
                        if set_damping_ratio <= 1 and set_damping_ratio >= 0.01:
                            lines.insert(
                                line_index + 2, "M593 D%s" % (set_damping_ratio)
                            )
                        self._set_freq(freq_options, lines, line_index, startfreq)
                    if _curent_layer == _step_height:
                        self._set_freq(freq_options, lines, line_index, startfreq)
                        startfreq += step_delta_freq
                        _step_height += step_height
                    _curent_layer += 1
            result = "\n".join(lines)
            data[layer_index] = result
        return data
