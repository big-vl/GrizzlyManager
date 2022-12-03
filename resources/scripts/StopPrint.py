# ------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   big-vl
# Date:     November 30, 2022
#
# Description:  postprocessing-script stop print at layer
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


class StopPrint(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Stop print",
            "key": "StopPrint",
            "metadata": {},
            "version": 2,
            "settings": {
                "stoplayer": {
                    "label": "Layer stop print",
                    "description": "If the print stop",
                    "type": "int",
                    "default_value": 0
                }
            }
        }"""

    def execute(self, data):
        stoplayer = int(self.getSettingValueByKey("stoplayer"))
        _curent_layer = 0
        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                line_index = lines.index(line)
                if line.startswith(";LAYER:"):
                    if _curent_layer == stoplayer:
                        lines.insert(_curent_layer, "M1001;")
                    _curent_layer += 1
            result = "\n".join(lines)
            data[layer_index] = result
        return data
