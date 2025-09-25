import FreeCAD
import os

class CanoeWorkbench:
    def __init__(self):
        self.__class__.Icon = self._icon_path()
        self.__class__.MenuText = "CanoeWB"
        self.__class__.ToolTip = "Canoe Generator Workbench (NACA 0009)"

    def _icon_path(self):
        here = os.path.dirname(__file__)
        return os.path.join(here, "resources", "icons", "canoe.svg")

    def Initialize(self):
        import FreeCADGui
        # Importera och registrera kommandot
        from .commands.CmdGenerateCanoe import COMMAND_NAME
        # Bara att importera modulen laddar FreeCADGui.addCommand i den filen
        import importlib; importlib.import_module(".commands.CmdGenerateCanoe", __package__)
        self.appendToolbar("CanoeWB", [COMMAND_NAME])
        self.appendMenu("CanoeWB", [COMMAND_NAME])

    def Activated(self):
        pass

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"
