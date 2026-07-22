from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton
)


class PrivacyDialog(QDialog):

    def __init__(self, browser):
        super().__init__(browser)

        self.browser = browser

        self.setWindowTitle(
            "Privacy Protection"
        )

        self.resize(200, 100)

        # منع الخط المايل في شباك الخصوصية بالكامل
        base_font = self.font()
        base_font.setItalic(False)
        self.setFont(base_font)

        # إجبار جميع الأزرار والعناصر على الخط العادي
        self.setStyleSheet("""
            QWidget {
                font-style: normal;
            }
            QPushButton {
                font-style: normal;
                font-weight: normal;
                padding: 6px 14px;
            }
            QCheckBox {
                font-style: normal;
            }
        """)

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("ᗢ Tracking Protection")
        )

        self.protection = QCheckBox(
            "Enable protection"
        )

        self.protection.setChecked(
            self.browser.adblocker.enabled
        )

        self.protection.stateChanged.connect(
            self.toggle_protection
        )

        layout.addWidget(
            self.protection
        )

        close = QPushButton(
            "Close"
        )

        close.clicked.connect(
            self.close
        )

        layout.addWidget(
            close
        )

        self.setLayout(
            layout
        )

    def toggle_protection(self):

        enabled = self.protection.isChecked()

        # enable/disable adblocker
        self.browser.adblocker.enabled = enabled

        # save setting
        self.browser.settings.privacy[
            "block_trackers"
        ] = enabled

        self.browser.settings.save()