from PyQt6.QtWidgets import QTabWidget, QPushButton, QStyle
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor


class BrowserTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        
        # Create a simple X icon for close button
        self._create_close_icon()

        self.add_tab_button = QPushButton("+", self)
        self.add_tab_button.setFixedSize(28, 28)
        self.add_tab_button.setToolTip("New Tab")
        self.add_tab_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_tab_button.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #e8eaed; font-weight: bold; }"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.08); }"
        )
        self.setCornerWidget(self.add_tab_button, Qt.Corner.TopRightCorner)

    def _create_close_icon(self):
        """Create a simple X icon for the close button."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#e8eaed"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawLine(3, 3, 13, 13)
        painter.drawLine(13, 3, 3, 13)
        painter.end()
        self.close_icon = QIcon(pixmap)

    def tabBar(self):
        """Override to apply close button styling."""
        return super().tabBar()

    def set_add_tab_callback(self, callback):
        self.add_tab_button.clicked.connect(callback)
