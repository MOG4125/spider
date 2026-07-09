import sys
import json
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMainWindow
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
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        # Add a node
        self.node = SpiderNode(100, 100, "Effect 1")
        self.scene.addItem(self.node)

    def export_patch(self, filename="patch.spdr"):
        # Save node position to .spdr file
        data = {"x": self.node.pos().x(), "y": self.node.pos().y()}
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Exported to {filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpiderApp()
    window.show()
    # Trigger export
    window.export_patch()
    sys.exit(app.exec())
