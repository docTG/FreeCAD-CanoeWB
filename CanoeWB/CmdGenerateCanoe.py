import math
import FreeCAD, Part
import FreeCADGui

from PySide2 import QtWidgets

COMMAND_NAME = "CanoeWB_GenerateCanoe"

def naca_00xx_thickness(x, t):
    """
    NACA 00xx halvtjocklek (yt) som funktion av x i [0,1].
    t = tjockleksparameter, t.ex. 0.09 för 0009.
    Formeln är standard: yt = 5*t*(...).
    """
    return 5.0 * t * (
        0.2969*math.sqrt(max(x, 0.0))
        - 0.1260*x
        - 0.3516*(x**2)
        + 0.2843*(x**3)
        - 0.1015*(x**4)
    )

def naca_outline_points(chord_len, beam, n=201, t=0.09):
    """
    Generera en sluten profil (ovansida + undersida) i XY-planet.
    chord_len = totallängd (L)
    beam = maximal totalbredd (B)
    n = antal punkter längs halva profilen (inkludera 0 och 1)
    t = 0.09 för NACA 0009
    Vi skalar tjockleken så att 2*yt_max == beam.
    """
    # Hitta max yt för normaliserad profil
    xs = [i/(n-1) for i in range(n)]
    yts = [naca_00xx_thickness(x, t) for x in xs]
    yt_max = max(yts) if yts else 1e-9
    if yt_max <= 0:
        yt_max = 1e-9
    scale_y = (beam/2.0) / yt_max

    # Bygg övre (positiv y) från nos (x=0) till akter (x=1)
    upper = []
    for x, yt in zip(xs, yts):
        X = (x - 0.5) * chord_len     # centrera längs X
        Y = yt * scale_y
        upper.append(FreeCAD.Vector(X, Y, 0.0))

    # Bygg undre (negativ y) från akter (x=1) tillbaka till nos (x=0)
    lower = []
    for x, yt in reversed(list(zip(xs, yts))):
        X = (x - 0.5) * chord_len
        Y = -yt * scale_y
        lower.append(FreeCAD.Vector(X, Y, 0.0))

    # Slut en enkel kontur
    pts = upper + lower
    return pts

class CanoeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Canoe (NACA 0009)")

        self.lengthEdit = QtWidgets.QLineEdit("5.0")   # meter
        self.beamEdit   = QtWidgets.QLineEdit("0.8")   # meter
        self.samplesEdit= QtWidgets.QLineEdit("201")   # upplösning

        form = QtWidgets.QFormLayout()
        form.addRow("Total längd (m):", self.lengthEdit)
        form.addRow("Max bredd (m):",   self.beamEdit)
        form.addRow("Punktantal:",      self.samplesEdit)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(btns)

    def values(self):
        try:
            L = float(self.lengthEdit.text())
            B = float(self.beamEdit.text())
            N = int(self.samplesEdit.text())
        except Exception:
            L, B, N = 5.0, 0.8, 201
        return L, B, N

class _CmdGenerateCanoe:
    def GetResources(self):
        import os
        moddir = FreeCAD.getHomePath()  # fallback om något strular
        try:
            moddir = __file__
            for _ in range(3):
                moddir = os.path.dirname(moddir)
            icon = os.path.join(moddir, "resources", "icons", "canoe.svg")
        except Exception:
            icon = ""
        return {
            "Pixmap": icon,
            "MenuText": "Generate Canoe (NACA 0009)",
            "ToolTip": "Skapa en kanotplanform i XY baserat på total längd och maxbredd."
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("Canoe")
        # Enkel dialog för parametrar
        dlg = CanoeDialog()
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        L, B, N = dlg.values()
        if L <= 0 or B <= 0 or N < 11:
            FreeCAD.Console.PrintError("Ogiltiga parametrar.\n")
            return

        pts = naca_outline_points(L, B, n=N, t=0.09)
        wire = Part.makePolygon(pts + [pts[0]])  # stäng konturen
        obj = doc.addObject("Part::Feature", "CanoePlanform")
        obj.Shape = wire
        obj.Label = f"Canoe L={L:.3f}m B={B:.3f}m (NACA0009)"
        doc.recompute()
        FreeCADGui.ActiveDocument.ActiveView.viewTop()
        FreeCADGui.SendMsgToActiveView("ViewFit")

FreeCADGui.addCommand(COMMAND_NAME, _CmdGenerateCanoe())
