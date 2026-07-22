from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QKeySequence
import os
import sys
from pathlib import Path
from ui.toolbar import BrowserToolBar
from ui.tabs import BrowserTabWidget
from ui.theme import load_stylesheet
from bookmarks import BookmarkManager, BookmarksDialog
from downloads import DownloadsManager
from history import HistoryManager, HistoryDialog
from settings import SettingsManager
from tab import BrowserTab
from shortcuts import register_shortcuts
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInfo
from adblocker import AdBlocker
from browser_profile import setup_profile
from fingerprint import install_fingerprint_protection
from privacy import PrivacyDialog


def get_asset_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        base_path = sys.MEIPASS if hasattr(sys, 'MEIPASS') else getattr(sys, '_MEIPASS')
    else:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class BrowserWindow(QMainWindow):

    def __init__(self, settings: SettingsManager):
        super().__init__()
  
        # Set absolute path for local landing page using PyInstaller-safe resolver
        STARTPAGE_PATH = get_asset_path("assets/startpage.html")
        STARTPAGE_URL = QUrl.fromLocalFile(STARTPAGE_PATH).toString()
        
        self.settings = settings
        self.settings.homepage = STARTPAGE_URL         
        self.setWindowTitle("Plus Browser")
        self.resize(1280, 840)
        self.setStyleSheet(load_stylesheet(self.settings.accent_color))

        # Flag to track download triggers
        self._is_downloading = False
        self.closed_tabs = []
        self.bookmark_manager = BookmarkManager()
        self.history_manager = HistoryManager()
        self.downloads_manager = DownloadsManager(self)

        # Profile setup & fingerprint protection
        self.profile = QWebEngineProfile("PlusBrowser", self)
        setup_profile(self.profile)
        install_fingerprint_protection(self.profile)

        # Enable local content cross-origin permissions
        profile_settings = self.profile.settings()
        profile_settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        profile_settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )

        # Download handling
        self.profile.downloadRequested.connect(self._on_download_requested)

        # AdBlocker setup
        self.adblocker = AdBlocker()
        self.profile.setUrlRequestInterceptor(self.adblocker)

        # Tab widget setup
        self.tabs = BrowserTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.change_tab)
        self.tabs.set_add_tab_callback(self.new_tab)
        self.setCentralWidget(self.tabs)

        # Toolbar & dialogs
        self.toolbar = BrowserToolBar(self)
        self.addToolBar(self.toolbar)
        self.url_bar = self.toolbar.url_bar
        self.privacy_window = PrivacyDialog(self)
        
        # Pass self.open_tab as callback for double-clicks in the dialog
        self.bookmarks_window = BookmarksDialog(self.bookmark_manager, open_callback=self.open_tab, parent=self)
        self.history_window = HistoryDialog(self.history_manager, self)

        register_shortcuts(self)
        # Bookmarks
        # Single initial tab load
        self.add_tab(self.settings.homepage, title="New Tab")

    def _on_download_requested(self, download):
        self._is_downloading = True
        self.downloads_manager.handle_download(download)

    def add_tab(self, url: str = None, title: str = "New Tab"):
        browser = BrowserTab(self.profile)
        
        # Ensure scheme is present if loading an external URL
        target_url = url or self.settings.homepage
        if not target_url.startswith(("http://", "https://", "file://", "about:")):
            target_url = "https://" + target_url

        browser.setUrl(QUrl(target_url))
        browser.urlChanged.connect(
            lambda new_url, b=browser: self.update_url(new_url, b)
        )
        browser.loadFinished.connect(
            lambda success, b=browser: self.on_load_finished(success, b)
        )
        browser.titleChanged.connect(lambda _, b=browser: self.update_title(b))

        index = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(index)
        self.toolbar.refresh()
        return browser

    def current_browser(self):
        return self.tabs.currentWidget()

    def new_tab(self):
        self.add_tab(self.settings.homepage, title="New Tab")

    def open_tab(self, url: str):
        self.add_tab(url, title="New Tab")

    def navigate(self):
        browser = self.current_browser()
        if browser is None:
            return

        raw = self.url_bar.text().strip()
        if not raw:
            return

        if " " in raw or "." not in raw:
            encoded_query = QUrl.toPercentEncoding(raw).data().decode("utf-8")
            search_str = f"https://www.google.com/search?q={encoded_query}"
            browser.setUrl(QUrl.fromUserInput(search_str))
            return

        browser.setUrl(QUrl.fromUserInput(raw))

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
        url_str = url.toString()

        if index >= 0:
            if url_str == self.settings.homepage:
                self.tabs.setTabText(index, "New Tab")
            else:
                self.tabs.setTabText(index, browser.page().title() or url_str)

        if browser == self.current_browser():
            if url_str == self.settings.homepage:
                self.url_bar.clear()
            else:
                self.url_bar.setText(url_str)
            self.toolbar.refresh()

    def update_title(self, browser: QWebEngineView):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            if browser.url().toString() == self.settings.homepage:
                self.tabs.setTabText(index, "New Tab")
            else:
                self.tabs.setTabText(index, browser.page().title() or "New Tab")

    def on_load_finished(self, success: bool, browser: QWebEngineView):
        if browser != self.current_browser():
            return

        self.toolbar.refresh()

        if success:
            url_str = browser.url().toString()
            # Do not save local landing page visits to history
            if url_str and url_str != "about:blank" and url_str != self.settings.homepage:
                self.history_manager.add_entry(url_str, browser.page().title())

    def change_tab(self, index: int):
        browser = self.current_browser()
        if browser is None:
            self.url_bar.clear()
            return

        url_str = browser.url().toString()
        if url_str == self.settings.homepage:
            self.url_bar.clear()
        else:
            self.url_bar.setText(url_str)

        self.toolbar.refresh()

    def close_tab(self, index: int):
        if self.tabs.count() <= 1:
            return

        browser = self.tabs.widget(index)
        if browser:
            url_str = browser.url().toString()
            if url_str != self.settings.homepage:
                self.closed_tabs.append(
                    (url_str, browser.page().title() or "New Tab")
                )
        self.tabs.removeTab(index)
        self.toolbar.refresh()

    def reopen_closed_tab(self):
        if not self.closed_tabs:
            return

        url, title = self.closed_tabs.pop()
        self.add_tab(url, title=title)

    def open_bookmarks_dialog(self):
        self.bookmarks_window.update_bookmarks()
        self.bookmarks_window.show()
        self.bookmarks_window.raise_()
        self.bookmarks_window.activateWindow()

    def open_bookmarks_menu(self):
        self.open_bookmarks_dialog()
        
    def bookmark_current_page(self):
        current_web = self.current_browser()
        if current_web:
            title = current_web.page().title() or current_web.url().toString()
            url = current_web.url().toString()
            if url and url != self.settings.homepage:
                self.bookmark_manager.add_bookmark(title, url)

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
            self.setWindowState(
                self.windowState() & ~Qt.WindowState.WindowFullScreen
            )
        else:
            self.setWindowState(
                self.windowState() | Qt.WindowState.WindowFullScreen
            )

    def open_downloads(self):
        self.downloads_manager.show_window()

    def open_settings(self):
        QMessageBox.information(
            self, "Settings", "Settings will be available in the next update."
        )