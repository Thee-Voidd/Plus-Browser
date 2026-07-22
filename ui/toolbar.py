from PyQt6.QtWidgets import QToolBar, QToolButton, QLineEdit, QMenu
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import QSize, Qt


class BrowserToolBar(QToolBar):
    def __init__(self, browser):
        super().__init__("Plus Browser Toolbar")
        self.browser = browser
        self.setIconSize(QSize(20, 20))
        self.setMovable(False)

        # 1. Back / Forward Buttons with clean delayed popup menus
        self.back_button = self._create_history_button("←", "Back", self.browser.go_back)
        self.forward_button = self._create_history_button("→", "Forward", self.browser.go_forward)

        # 2. Main Navigation Controls
        self.reload_action = QAction("⟳", self)
        self.reload_action.setToolTip("Reload")
        self.reload_action.triggered.connect(self.browser.reload_page)
        self.addAction(self.reload_action)

        self.stop_action = QAction("⏸︎", self)
        self.stop_action.setToolTip("Stop")
        self.stop_action.triggered.connect(self.browser.stop_loading)
        self.addAction(self.stop_action)

        self.home_action = QAction("⌂", self)
        self.home_action.setToolTip("Home")
        self.home_action.triggered.connect(self.browser.go_home)
        self.addAction(self.home_action)

        self.new_tab_action = QAction("+", self)
        self.new_tab_action.setToolTip("New Tab")
        self.new_tab_action.triggered.connect(self.browser.new_tab)
        self.addAction(self.new_tab_action)             
        
        self.addSeparator()

        # 3. URL Bar
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.browser.navigate)
        self.addWidget(self.url_bar)

        # 4. Shield / Privacy Action
        self.shield_action = QAction("ᗢ", self)  # Swapped unicode shield symbol for visual clarity
        self.shield_action.setToolTip("Privacy Protection")
        self.shield_action.triggered.connect(self.browser.open_privacy)
        self.addAction(self.shield_action)   

        self.addSeparator()

        # 5. Bookmarks Action
        self.bookmark_page_action = QAction("★", self)
        self.bookmark_page_action.setToolTip("Bookmark current page")
        self.bookmark_page_action.triggered.connect(self.browser.bookmark_current_page)
        self.addAction(self.bookmark_page_action)

        # 6. Hamburger Menu
        self.menu_button = QToolButton(self)
        self.menu_button.setIcon(self._create_hamburger_icon())
        self.menu_button.setIconSize(QSize(20, 20))
        self.menu_button.setToolTip("Menu")
        self.menu_menu = QMenu(self.menu_button)
        self.menu_menu.addAction("Bookmarks", self.browser.open_bookmarks_menu)
        self.menu_menu.addAction("History", self.browser.open_history)
        self.menu_menu.addAction("Downloads", self.browser.open_downloads)
        
        # Proper popup mapping
        self.menu_button.setMenu(self.menu_menu)
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.addWidget(self.menu_button)

    def _create_hamburger_icon(self):
        """Create a hamburger menu icon (three horizontal lines)."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#e8eaed"))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawLine(3, 5, 17, 5)
        painter.drawLine(3, 10, 17, 10)
        painter.drawLine(3, 15, 17, 15)
        painter.end()
        return QIcon(pixmap)

    def _create_history_button(self, text, tooltip, callback):
        """Creates a sleek tool button that clicks normally and shows history on hold/menu."""
        button = QToolButton(self)
        button.setText(text)
        button.setToolTip(tooltip)
        
        # DelayedPopup prevents Qt from rendering separate drop-arrow columns
        button.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)
        button.clicked.connect(callback)
        
        menu = QMenu(button)
        button.setMenu(menu)
        self.addWidget(button)
        return button

    def refresh(self):
        browser = self.browser.current_browser()
        if browser is None:
            return

        history = browser.history()
        self.back_button.setEnabled(history.canGoBack())
        self.forward_button.setEnabled(history.canGoForward())
        self._populate_history_menu(self.back_button.menu(), history.backItems(8))
        self._populate_history_menu(self.forward_button.menu(), history.forwardItems(8))

    def _populate_history_menu(self, menu, items):
        menu.clear()
        for entry in items:
            action = menu.addAction(entry.title() or entry.url().toString())
            action.triggered.connect(lambda checked, u=entry.url().toString(): self.browser.open_tab(u))