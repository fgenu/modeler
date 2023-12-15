from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QAction

from mycanvas import *
from mymodel import *


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Modeler")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)
        # create a Toolbar
        tb = self.addToolBar("File")
        tb.addAction(QAction(QIcon("icons/save.png"), "save", self))
        tb.addAction(QAction(QIcon("icons/mesh.png"), "generate mesh", self))
        tb.addAction(QAction(QIcon("icons/fit.png"), "fit", self))
        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self, a):
        if a.text() == "generate mesh":
            self.canvas.mesh = self.generate_mesh()
            self.canvas.update()
            self.canvas.repaint()
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "save":
            self.save_mesh()

    def generate_mesh(self, spacing=25):
        x_min, x_max, y_min, y_max = self.canvas.m_model.getBoundBox()
        mesh = []
        for x in range(int(x_min), int(x_max) + spacing, spacing):
            for y in range(int(y_min), int(y_max) + spacing, spacing):
                point = MyPoint(x, y)
                if self.is_point_inside(point):
                    # Store the point and its valid neighbors
                    neighbors = []
                    for dx, dy in [(-spacing, 0), (spacing, 0), (0, -spacing), (0, spacing)]:
                        nx, ny = x + dx, y + dy
                        neighbor_candidate = MyPoint(nx, ny)
                        if self.is_point_inside(neighbor_candidate):
                            neighbors.append(neighbor_candidate)
                    mesh.append((point, neighbors))
        return mesh

    def is_point_inside(self, point):
        for patch in self.canvas.m_hmodel.getPatches():
            if patch.isPointInside(point):
                return True
        return False


    def save_mesh(self):
        print("Saving mesh")
        with open("mesh.json", "w") as file:
            file.write("{ \"points\": [")
            delimiter = ""
            for point, _ in self.canvas.mesh:
                x, y = point.getX(), point.getY()
                file.write(f"{delimiter} [{x}, {y}]")
                delimiter = ","
            file.write(" ],\n")
            arr_delimiter = ""
            file.write(" \"neighbourhoods\": [\n")
            for i in range(len(self.canvas.mesh)):
                file.write(f"{arr_delimiter}[")
                arr_delimiter = ",\n"
                delimiter = ""
                for j in range(len(self.canvas.mesh)):
                    if self.point_in_list(self.canvas.mesh[j][0], self.canvas.mesh[i][1]):
                        file.write(f"{delimiter} {j}")
                        delimiter = ","
                file.write(" ]")
            file.write(" ] }")

    def point_in_list(self, point: MyPoint, list):
        for p in list:
            if p.getX() == point.getX() and p.getY() == point.getY():
                return True
        return False
