from PyQt6.QtGui import QShortcut, QKeySequence


def register_shortcuts(window):
    QShortcut(QKeySequence("Ctrl+T"), window, activated=window.new_tab)
    QShortcut(QKeySequence("Ctrl+W"), window, activated=lambda: window.close_tab(window.tabs.currentIndex()))
    QShortcut(QKeySequence("Ctrl+Shift+T"), window, activated=window.reopen_closed_tab)
    QShortcut(QKeySequence("Ctrl+Tab"), window, activated=lambda: window.tabs.setCurrentIndex((window.tabs.currentIndex() + 1) % window.tabs.count()))
    QShortcut(QKeySequence("Ctrl+Shift+Tab"), window, activated=lambda: window.tabs.setCurrentIndex((window.tabs.currentIndex() - 1) % window.tabs.count()))
    QShortcut(QKeySequence("Ctrl+L"), window, activated=lambda: window.url_bar.setFocus())
    QShortcut(QKeySequence("Ctrl+R"), window, activated=window.reload_page)
    QShortcut(QKeySequence("F5"), window, activated=window.reload_page)
    QShortcut(QKeySequence("Ctrl++"), window, activated=lambda: window.current_browser() and window.current_browser().setZoomFactor(window.current_browser().zoomFactor() + 0.1))
    QShortcut(QKeySequence("Ctrl+-"), window, activated=lambda: window.current_browser() and window.current_browser().setZoomFactor(max(window.current_browser().zoomFactor() - 0.1, 0.25)))
    QShortcut(QKeySequence("Ctrl+0"), window, activated=lambda: window.current_browser() and window.current_browser().setZoomFactor(1.0))
    QShortcut(QKeySequence("F11"), window, activated=window.toggleFullScreen)
