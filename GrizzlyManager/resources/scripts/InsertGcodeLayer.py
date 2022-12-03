# ------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   big-vl
# Date:     December 1, 2022
#
# Description:  postprocessing-script gcode at layer
#
#
# ------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 1/12/2022
# ------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Application import Application
from UM.Logger import Logger

__version__ = "1.0"


class InsertGcodeLayer(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Gcode at layer",
            "key": "gcodelayer",
            "metadata": {},
            "version": 2,
            "settings": {
                "insertlayer": {
                    "label": "Layer gcode",
                    "description": "Insert gcode at layer",
                    "type": "int",
                    "default_value": 0
                },
                "gcodevalue": {
                    "label": "Gcode value",
                    "description": "Insert gcode",
                    "type": "str"
                }
            }
        }"""

    def execute(self, data):
        insertlayer = int(self.getSettingValueByKey("insertlayer"))
        gcodevalue = int(self.getSettingValueByKey("gcodevalue"))
        _curent_layer = 0
        for layer in data:
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                line_index = lines.index(line)
                if line.startswith(";LAYER:"):
                    if _curent_layer == insertlayer:
                        lines.insert(_curent_layer, "%s;" % (gcodevalue))
                    _curent_layer += 1
            result = "\n".join(lines)
            data[layer_index] = result
        return data
