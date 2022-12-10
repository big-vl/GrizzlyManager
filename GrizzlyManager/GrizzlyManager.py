# -----------------------------------------------------------------------------------
# Grizzly Manager Copyright (c) 2022 big-vl
# -----------------------------------------------------------------------------------
# V1.00    : https://github.com/big-vl/GrizzlyManager/wiki
# -------------------------------------------------------------------------------------------

VERSION_QT5 = False
try:
    from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt6.QtGui import QDesktopServices
except ImportError:
    from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt5.QtGui import QDesktopServices

    VERSION_QT5 = True

# Imports from the python standard library to build the plugin functionality
import os
import sys
import re
import math
import numpy
import trimesh
import shutil
from shutil import copyfile

from typing import Optional, List

from UM.Extension import Extension
from UM.PluginRegistry import PluginRegistry
from UM.Application import Application
from cura.CuraApplication import CuraApplication

from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Resources import Resources
from UM.Settings.SettingInstance import SettingInstance
from cura.Scene.CuraSceneNode import CuraSceneNode
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Operations.SetTransformOperation import SetTransformOperation

from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Version import Version

from UM.Logger import Logger
from UM.Message import Message

from UM.i18n import i18nCatalog

catalog = i18nCatalog("cura")
i18n_cura_catalog = i18nCatalog("cura")
i18n_catalog = i18nCatalog("fdmprinter.def.json")
i18n_extrud_catalog = i18nCatalog("fdmextruder.def.json")


# This class is the extension and doubles as QObject to manage the qml
class GrizzlyManager(QObject, Extension):
    # Create an api
    api = CuraApplication.getInstance().getCuraAPI()

    def __init__(self, parent=None) -> None:
        self._file = [
            "InputShapingZeta.py",
            "InputShapingWhile.py",
            "StopPrint.py",
            "InsertGcodeLayer.py"
        ]
        QObject.__init__(self, parent)
        Extension.__init__(self)
        # set the preferences to store the default value
        self._preferences = CuraApplication.getInstance().getPreferences()
        Resources.addSearchPath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
        )

        Logger.log("d", "Info CuraVersion --> " + str(CuraVersion))

        if "master" in CuraVersion:
            self.Major = 4
            self.Minor = 20
        else:
            try:
                self.Major = int(CuraVersion.split(".")[0])
                self.Minor = int(CuraVersion.split(".")[1])
            except:
                pass

        self._controller = CuraApplication.getInstance().getController()
        self._message = None

        self.setMenuName(catalog.i18nc("@item:inmenu", "GrizzlyManager"))
        self.addMenuItem(
            catalog.i18nc("@item:inmenu", "Add a Ringing Tower"), self.addRingingTower
        )
        self.addMenuItem(
            catalog.i18nc("@item:inmenu", "Add a Calibration Cube"),
            self.addCalibrationCube,
        )
        self.addMenuItem(
            catalog.i18nc("@item:inmenu", "Add a Calibration Temp 260-230 (PETG)"),
            self.addCalibrationTempTower260_230,
        )
        self.addMenuItem("", lambda: None)
        self.addMenuItem(
            catalog.i18nc("@item:inmenu", "Add a Cube holder"),
            self.addCubeHolder,
        )
        self.addMenuItem(
            catalog.i18nc("@item:inmenu", "Add a Grizzly Bear"), self.addGrizzlyBear
        )
        self.addMenuItem("  ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "About"), self.gotoHelp)

    # Checker version from github
    def checkUpdateVersion(self):
        try:
            import requests

            url = (
                "https://raw.githubusercontent.com/big-vl/GrizzlyManager/master/VERSION"
            )
            data = requests.get(url, verify=False)
            version = data.text
            gm_ver = "1.1"
            if str(version).strip() != gm_ver:
                title = catalog.i18nc("@info:title", "NEW VERSION ! GrizzlyManager:")
                text = (
                    "\n\nCurrent version: %s\nNew version : %s\n\n Please update: Grizzly Manager"
                    % (gm_ver, str(version))
                )
                if self.Major == 4 and self.Minor < 11:
                    Message(
                        title=title,
                        text=text,
                    ).show()
                else:
                    Message(
                        title=title,
                        text=text,
                        message_type=Message.MessageType.WARNING,
                    ).show()
        except Exception as e:
            self.writeToLog(e)

    # ===== Text Output ===================================================================================================
    # writes the message to the log, includes timestamp, length is fixed
    def writeToLog(self, str):
        Logger.log("d", "Debug GrizzlyManager = %s", str)

    def gotoHelp(self) -> None:
        QDesktopServices.openUrl(QUrl("https://github.com/big-vl/GrizzlyManager/wiki"))

    def _registerShapeStl(self, mesh_name, mesh_filename=None, **kwargs) -> None:
        if mesh_filename is None:
            mesh_filename = mesh_name + ".stl"

        model_definition_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "models", mesh_filename
        )
        mesh = trimesh.load(model_definition_path)
        self._addShape(mesh_name, self._toMeshData(mesh), **kwargs)

    # ----------------------------------------------------------
    # Check material_linear_advance_enable must be False
    # ----------------------------------------------------------
    def _checkAccelerationEnabled(self, val):
        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        extruder_stack = (
            CuraApplication.getInstance()
            .getExtruderManager()
            .getActiveExtruderStacks()[0]
        )
        if global_container_stack.getProperty(
            "acceleration_enabled", "value"
        ):
            key = "acceleration_enabled"
            definition_key = key + " label"
            untranslated_label = extruder_stack.getProperty(key, "label")
            translated_label = i18n_catalog.i18nc(definition_key, untranslated_label)
            title = catalog.i18nc("@info:title", "Warning ! GrizzlyManager:")
            if self.Major == 4 and self.Minor < 11:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value: %s"
                    % (translated_label, str(val)),
                ).show()
            else:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value: %s"
                    % (translated_label, str(val)),
                    message_type=Message.MessageType.WARNING,
                ).show()
            # Define material_linear_advance_enable: False
            global_container_stack.setProperty(
                "acceleration_enabled", "value", val
            )

    # ----------------------------------------------------------
    # Check material_linear_advance_enable must be False
    # ----------------------------------------------------------
    def _checkLinearAdvance(self, val):
        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        extruder_stack = (
            CuraApplication.getInstance()
            .getExtruderManager()
            .getActiveExtruderStacks()[0]
        )
        if global_container_stack.getProperty(
            "material_linear_advance_enable", "value"
        ):
            key = "material_linear_advance_enable"
            definition_key = key + " label"
            untranslated_label = extruder_stack.getProperty(key, "label")
            translated_label = i18n_catalog.i18nc(definition_key, untranslated_label)
            title = catalog.i18nc("@info:title", "Warning ! GrizzlyManager:")
            if self.Major == 4 and self.Minor < 11:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value: %s"
                    % (translated_label, str(val)),
                ).show()
            else:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value: %s"
                    % (translated_label, str(val)),
                    message_type=Message.MessageType.WARNING,
                ).show()
            # Define material_linear_advance_enable: False
            global_container_stack.setProperty(
                "material_linear_advance_enable", "value", val
            )

    # ----------------------------------------------------------
    # Check adaptive_layer_height_enabled must be False
    # ----------------------------------------------------------
    def _checkAdaptativ(self, val):
        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        extruder_stack = (
            CuraApplication.getInstance()
            .getExtruderManager()
            .getActiveExtruderStacks()[0]
        )
        adaptive_layer = global_container_stack.getProperty(
            "adaptive_layer_height_enabled", "value"
        )
        extruder = global_container_stack.extruderList[0]

        if adaptive_layer is not val:
            key = "adaptive_layer_height_enabled"
            definition_key = key + " label"
            untranslated_label = extruder_stack.getProperty(key, "label")
            translated_label = i18n_catalog.i18nc(definition_key, untranslated_label)
            title = catalog.i18nc("@info:title", "Warning ! GrizzlyManager:")
            if self.Major == 4 and self.Minor < 11:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s\nNew value : %s"
                    % (translated_label, str(val)),
                ).show()
            else:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s\nNew value : %s"
                    % (translated_label, str(val)),
                    message_type=Message.MessageType.WARNING,
                ).show()
            # Define adaptive_layer
            global_container_stack.setProperty(
                "adaptive_layer_height_enabled", "value", False
            )

    # ----------------------------------------------------------
    # Check magic_spiralize must be True
    # ----------------------------------------------------------
    def _checkMagicSpiralize(self, val):
        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        extruder_stack = (
            CuraApplication.getInstance()
            .getExtruderManager()
            .getActiveExtruderStacks()[0]
        )
        if not global_container_stack.getProperty("magic_spiralize", "value"):
            key = "magic_spiralize"
            definition_key = key + " label"
            untranslated_label = extruder_stack.getProperty(key, "label")
            translated_label = i18n_catalog.i18nc(definition_key, untranslated_label)
            title = catalog.i18nc(
                "@info:title",
                "Warning ! GrizzlyManager: Use model for calibrate Input Shaping",
            )
            if self.Major == 4 and self.Minor < 11:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value : %s"
                    % (translated_label, str(val)),
                ).show()
            else:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value : %s"
                    % (translated_label, str(val)),
                    message_type=Message.MessageType.WARNING,
                ).show()
            # Define material_linear_advance_enable: False
            global_container_stack.setProperty("magic_spiralize", "value", val)

    # ----------------------------------------------------------
    # Set bottom_layers = value
    # ----------------------------------------------------------
    def _setBottomLayers(self, val):
        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        extruder_stack = (
            CuraApplication.getInstance()
            .getExtruderManager()
            .getActiveExtruderStacks()[0]
        )
        bottom_layers_val = global_container_stack.getProperty("bottom_layers", "value")

        if bottom_layers_val == 0 or bottom_layers_val > 3:
            key = "bottom_layers"
            definition_key = key + " label"
            untranslated_label = extruder_stack.getProperty(key, "label")
            translated_label = i18n_catalog.i18nc(definition_key, untranslated_label)
            title = catalog.i18nc(
                "@info:title",
                "Warning ! GrizzlyManager: Use model for calibrate Input Shaping",
            )
            if self.Major == 4 and self.Minor < 11:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value : %s"
                    % (translated_label, str(val)),
                ).show()
            else:
                Message(
                    title=title,
                    text="! Modification ! in the current profile of : %s \nNew value : %s"
                    % (translated_label, str(val)),
                    message_type=Message.MessageType.INFORMATION,
                ).show()
            # Define bottom_layers: False
            global_container_stack.setProperty("bottom_layers", "value", val)

    def addCubeHolder(self) -> None:
        self.checkUpdateVersion()
        self._registerShapeStl("XYZ_Base")
        self._registerShapeStl("XYZ_Pole")

    def addGrizzlyBear(self) -> None:
        self._registerShapeStl("GrizzlyBear")
        self.checkUpdateVersion()

    def addCalibrationTempTower260_230(self) -> None:
        self._registerShapeStl("TempTowerPETG260_230")
        self.checkUpdateVersion()

    def addCalibrationCube(self) -> None:
        self._registerShapeStl("CalibrationCube")
        self.checkUpdateVersion()

    def addRingingTower(self) -> None:
        self._registerShapeStl("RingingTower")
        self._checkAccelerationEnabled(False)
        self._checkLinearAdvance(False)
        self._checkMagicSpiralize(True)
        self._checkAdaptativ(False)
        self._setBottomLayers(2)
        self.checkUpdateVersion()

    # #----------------------------------------
    # # Initial Source code from  fieldOfView
    # #----------------------------------------
    def _toMeshData(self, tri_node: trimesh.base.Trimesh) -> MeshData:
        # Rotate the part to laydown on the build plate
        # Modification from 5@xes
        tri_node.apply_transform(
            trimesh.transformations.rotation_matrix(math.radians(90), [-1, 0, 0])
        )
        tri_faces = tri_node.faces
        tri_vertices = tri_node.vertices

        # Following Source code from  fieldOfView
        # https://github.com/fieldOfView/Cura-SimpleShapes/blob/bac9133a2ddfbf1ca6a3c27aca1cfdd26e847221/SimpleShapes.py#L45
        indices = []
        vertices = []

        index_count = 0
        face_count = 0
        for tri_face in tri_faces:
            face = []
            for tri_index in tri_face:
                vertices.append(tri_vertices[tri_index])
                face.append(index_count)
                index_count += 1
            indices.append(face)
            face_count += 1

        vertices = numpy.asarray(vertices, dtype=numpy.float32)
        indices = numpy.asarray(indices, dtype=numpy.int32)
        normals = calculateNormalsFromIndexedVertices(vertices, indices, face_count)

        mesh_data = MeshData(vertices=vertices, indices=indices, normals=normals)

        return mesh_data

    # # Initial Source code from  fieldOfView
    # # https://github.com/fieldOfView/Cura-SimpleShapes/blob/bac9133a2ddfbf1ca6a3c27aca1cfdd26e847221/SimpleShapes.py#L70
    def _addShape(
        self, mesh_name, mesh_data: MeshData, ext_pos=0, hole=False, thin=False
    ) -> None:
        application = CuraApplication.getInstance()
        global_stack = application.getGlobalContainerStack()
        if not global_stack:
            return

        node = CuraSceneNode()

        node.setMeshData(mesh_data)
        node.setSelectable(True)
        if len(mesh_name) == 0:
            node.setName("TestPart" + str(id(mesh_data)))
        else:
            node.setName(str(mesh_name))

        scene = self._controller.getScene()
        op = AddSceneNodeOperation(node, scene.getRoot())
        op.push()

        extruder_stack = application.getExtruderManager().getActiveExtruderStacks()

        extruder_nr = len(extruder_stack)
        Logger.log("d", "extruder_nr= %d", extruder_nr)
        # default_extruder_position  : <class 'str'>
        if ext_pos > 0 and ext_pos <= extruder_nr:
            default_extruder_position = int(ext_pos - 1)
        else:
            default_extruder_position = int(
                application.getMachineManager().defaultExtruderPosition
            )
        Logger.log(
            "d", "default_extruder_position= %s", type(default_extruder_position)
        )
        default_extruder_id = extruder_stack[default_extruder_position].getId()
        Logger.log("d", "default_extruder_id= %s", default_extruder_id)
        node.callDecoration("setActiveExtruder", default_extruder_id)

        stack = node.callDecoration(
            "getStack"
        )  # created by SettingOverrideDecorator that is automatically added to CuraSceneNode
        settings = stack.getTop()

        active_build_plate = application.getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))

        node.addDecorator(SliceableObjectDecorator())

        application.getController().getScene().sceneChanged.emit(node)
