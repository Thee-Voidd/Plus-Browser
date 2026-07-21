from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel


class BrowserSidebar(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Sidebar", parent)
        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.addWidget(QLabel("Bookmarks and History will appear here.", self))
        content.setLayout(layout)
        self.setWidget(content)
