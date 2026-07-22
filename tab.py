from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView


class BrowserTab(QWebEngineView):
    def __init__(self, profile):
        super().__init__()

        self.pinned = False

        page = QWebEnginePage(profile, self)
        self.setPage(page)
        