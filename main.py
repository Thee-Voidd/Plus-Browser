import sys
from PyQt6.QtWidgets import QApplication
from browser import BrowserWindow
from settings import SettingsManager
from browser_profile import setup_profile
def main():
    app = QApplication(sys.argv)
    settings = SettingsManager()
    window = BrowserWindow(settings)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
