from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.web = QWebEngineView()
        self.web.load(QUrl("http://127.0.0.1:8000"))
        self.setCentralWidget(self.web)

        nav = QToolBar("Navigation")
        self.addToolBar(nav)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.web.back)
        nav.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.web.forward)
        nav.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.web.reload)
        nav.addAction(reload_btn)

        self.setWindowTitle("System Resource Monitor")
        self.resize(1280, 800)

app = QApplication(sys.argv)
browser = Browser()
browser.show()
sys.exit(app.exec_())
