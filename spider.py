import sys
import json
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class SpiderNode(QGraphicsRectItem):
    def __init__(self, x, y, name):
        super().__init__(0, 0, 100, 50)
        self.setPos(x, y)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setBrush(Qt.GlobalColor.darkBlue)

class SpiderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spider Patcher App")
        self.resize(800, 600)
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Graphics View
        self.scene = QGraphicsScene(0, 0, 780, 500)
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)
        
        # Save Button
        self.btn = QPushButton("Export .spdr")
        self.btn.clicked.connect(self.export_patch)
        self.layout.addWidget(self.btn)
        
        # Add a node
        self.node = SpiderNode(100, 100, "Effect 1")
        self.scene.addItem(self.node)

    def export_patch(self):
        data = {"node_x": self.node.pos().x(), "node_y": self.node.pos().y()}
        with open("patch.spdr", 'w') as f:
            json.dump(data, f)
        print("Exported to patch.spdr")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpiderApp()
    window.show()
    # This line prevents the app from closing immediately
    sys.exit(app.exec())
