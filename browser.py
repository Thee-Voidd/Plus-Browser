from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QKeySequence

from ui.toolbar import BrowserToolBar
from ui.tabs import BrowserTabWidget
from ui.theme import load_stylesheet
from bookmarks import BookmarkManager, BookmarksDialog
from downloads import DownloadsManager
from history import HistoryManager, HistoryDialog
from settings import SettingsManager
from tab import BrowserTab
from shortcuts import register_shortcuts
from PyQt6.QtWebEngineCore import QWebEngineProfile
from adblocker import AdBlocker
from browser_profile import setup_profile
from fingerprint import install_fingerprint_protection
from privacy import PrivacyDialog
class BrowserWindow(QMainWindow):
    
    def __init__(self, settings: SettingsManager):

        super().__init__()
        self.settings = settings
        self.setWindowTitle("Plus Browser")
        self.resize(1280, 840)
        self.setStyleSheet(load_stylesheet(self.settings.accent_color))
        

        self.closed_tabs = []
        self.bookmark_manager = BookmarkManager()
        self.history_manager = HistoryManager()
        self.downloads_manager = DownloadsManager(self)
        #profile fingerprint proofing
        self.profile = QWebEngineProfile("PlusBrowser", self)
        setup_profile(self.profile)
        install_fingerprint_protection(self.profile)
        print(self.profile.httpUserAgent())
        self.profile.downloadRequested.connect(
        self.downloads_manager.handle_download
        )       
        
        self.adblocker = AdBlocker()
        #connects
        self.profile.setUrlRequestInterceptor(self.adblocker)

        self.tabs = BrowserTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.change_tab)
        self.tabs.set_add_tab_callback(self.new_tab)
        self.setCentralWidget(self.tabs)

        self.toolbar = BrowserToolBar(self)
        self.addToolBar(self.toolbar)
        self.url_bar = self.toolbar.url_bar
        self.privacy_window = PrivacyDialog(self)       
        self.bookmarks_window = BookmarksDialog(self.bookmark_manager, self)
        self.history_window = HistoryDialog(self.history_manager, self)

        register_shortcuts(self)
        self.add_tab(self.settings.homepage)


    def add_tab(self, url: str = None, title: str = "New Tab"):
        browser = BrowserTab(self.profile)
        browser.setUrl(QUrl(url or self.settings.homepage))
        browser.urlChanged.connect(lambda new_url, b=browser: self.update_url(new_url, b))
        browser.loadFinished.connect(lambda success, b=browser: self.on_load_finished(success, b))
        browser.titleChanged.connect(lambda _, b=browser: self.update_title(b))

        index = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(index)
        self.toolbar.refresh()
        return browser

    def current_browser(self):
        return self.tabs.currentWidget()

    def new_tab(self):
        self.add_tab(self.settings.homepage)

    def open_tab(self, url: str):
        self.add_tab(url, title=url)

    def navigate(self):
        browser = self.current_browser()
        if browser is None:
            return

        raw = self.url_bar.text().strip()
        if not raw:
            return

        if " " in raw or ("." not in raw and "." not in raw):
            search = self.settings.search_engine.format(raw)
            browser.setUrl(QUrl(search))
            return

        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw

        browser.setUrl(QUrl(raw))

    def go_back(self):
        browser = self.current_browser()
        if browser and browser.history().canGoBack():
            browser.back()

    def go_forward(self):
        browser = self.current_browser()
        if browser and browser.history().canGoForward():
            browser.forward()

    def reload_page(self):
        browser = self.current_browser()
        if browser:
            browser.reload()

    def stop_loading(self):
        browser = self.current_browser()
        if browser:
            browser.stop()

    def go_home(self):
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(self.settings.homepage))

    def update_url(self, url: QUrl, browser: QWebEngineView):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabText(index, browser.page().title() or url.toString())

        if browser == self.current_browser():
            self.url_bar.setText(url.toString())
            self.toolbar.refresh()

    def update_title(self, browser: QWebEngineView):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabText(index, browser.page().title() or "New Tab")

    def on_load_finished(self, success: bool, browser: QWebEngineView):
        if browser != self.current_browser():
            return

        self.toolbar.refresh()
        self.history_manager.add_entry(browser.url().toString(), browser.page().title())

        if not success:
            QMessageBox.warning(self, "Load failed", "The page did not finish loading.")

    def change_tab(self, index: int):
        browser = self.current_browser()
        if browser is None:
            self.url_bar.clear()
            return

        self.url_bar.setText(browser.url().toString())
        self.toolbar.refresh()

    def close_tab(self, index: int):
        if self.tabs.count() <= 1:
            return

        browser = self.tabs.widget(index)
        if browser:
            self.closed_tabs.append((browser.url().toString(), browser.page().title() or "New Tab"))
        self.tabs.removeTab(index)
        self.toolbar.refresh()

    def reopen_closed_tab(self):
        if not self.closed_tabs:
            return

        url, title = self.closed_tabs.pop()
        self.add_tab(url, title=title)

    def bookmark_current_page(self):
        browser = self.current_browser()
        if browser is None:
            return

        url = browser.url().toString()
        title = browser.page().title() or url
        self.bookmark_manager.add_bookmark(title, url)
        QMessageBox.information(self, "Bookmark added", f"{title} was added to bookmarks.")

    def open_bookmarks_menu(self):
        self.bookmarks_window.update_bookmarks()
        self.bookmarks_window.show()
        self.bookmarks_window.raise_()
        self.bookmarks_window.activateWindow()

    def open_history(self):
        self.history_window.update_history()
        self.history_window.show()
        self.history_window.raise_()
        self.history_window.activateWindow()
    def open_privacy(self):

        self.privacy_window.show()

        self.privacy_window.raise_()

        self.privacy_window.activateWindow()
    def toggleFullScreen(self):
        if self.windowState() & Qt.WindowState.WindowFullScreen:
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowFullScreen)
        else:
            self.setWindowState(self.windowState() | Qt.WindowState.WindowFullScreen)

    def open_downloads(self):
        self.downloads_manager.show_window()

    def open_settings(self):
        QMessageBox.information(self, "Settings", "Settings will be available in the next update.")
