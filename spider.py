import sys

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
    
    class SpiderApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Spider Patcher")
            self.resize(400, 300)
            
            # Simple UI to confirm it's working
            self.label = QLabel("Spider Patcher is running!")
            layout = QVBoxLayout()
            layout.addWidget(self.label)
            
            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)

    app = QApplication(sys.argv)
    window = SpiderApp()
    window.show()
    sys.exit(app.exec())

except Exception as e:
    # If the app crashes, this will pause and show you why
    input(f"The app crashed with this error:\n{e}\n\nPress Enter to close...")
