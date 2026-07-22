from PyQt6.QtWidgets import QTabWidget, QPushButton, QTabBar
from PyQt6.QtCore import Qt


class BrowserTabWidget(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(False)

        self.close_buttons = []

        self.setElideMode(
            Qt.TextElideMode.ElideRight
        )

        self.setStyleSheet("""
        QTabWidget::pane {
            border: none;
        }

        QTabBar {
            background: transparent;
        }

        QTabBar::tab {
            background: #1a1c20;
            color: #cfd5e0;
            height: 28px;
            min-width: 120px;
            padding-left: 10px;
            padding-right: 0px;
            margin-right: 2px;
        }

        QTabBar::tab:selected {
            background: #2b2e35;
            color: white;
        }

        QTabBar::tab:hover {
            background: #25282e;
        }
        """)

        self.currentChanged.connect(
            self.update_close_buttons
        )


    def addTab(self, widget, title):

        index = super().addTab(
            widget,
            title
        )

        close = QPushButton("✕")

        close.setFixedSize(
            28,
            28
        )

        close.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        close.setStyleSheet("""
        QPushButton {
            border: none;
            background: transparent;
            color: #e8eaed;
            font-size: 12px;
            font-weight: bold;
        }

        QPushButton:hover {
            background: rgba(255,255,255,0.18);
        }

        QPushButton:pressed {
            background: rgba(255,255,255,0.30);
        }
        """)


        # store tab index safely on the button
        close.tab_index = index


        close.clicked.connect(
            lambda checked=False, b=close:
            self.close_button_clicked(b)
        )


        self.close_buttons.append(close)


        self.tabBar().setTabButton(
            index,
            QTabBar.ButtonPosition.RightSide,
            close
        )


        self.update_close_buttons()

        return index



    def removeTab(self, index):

        # remove matching close button
        if 0 <= index < len(self.close_buttons):

            button = self.close_buttons.pop(index)

            button.deleteLater()


        # fix remaining button indexes
        for i, button in enumerate(self.close_buttons):
            button.tab_index = i


        super().removeTab(index)


        self.update_close_buttons()



    def update_close_buttons(self):

        current = self.currentIndex()

        for i, button in enumerate(self.close_buttons):

            if i == current:
                button.show()

            else:
                button.hide()



    def close_button_clicked(self, button):

        index = getattr(
            button,
            "tab_index",
            -1
        )

        if index >= 0:
            self.tabCloseRequested.emit(index)



    def set_add_tab_callback(self, callback):
        pass