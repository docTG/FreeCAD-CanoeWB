# InitGui.py: GUI-registrering av arbetsbänk och kommandon
import FreeCAD
try:
    import FreeCADGui
except Exception:
    FreeCAD.Console.PrintWarning("CanoeWB: GUI ej tillgängligt.\n")
else:
    from .CanoeWorkbench import CanoeWorkbench
    FreeCADGui.addWorkbench(CanoeWorkbench())
    FreeCAD.Console.PrintMessage("CanoeWB: InitGui klart\n")
