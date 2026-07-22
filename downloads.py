from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import Qt


class DownloadsManager:
    def __init__(self, parent=None):
        # 1. Use QDialog so it pops up as its own window instead of embedding into main UI
        self.window = QDialog(parent)
        self.window.setWindowTitle("Downloads")
        self.window.resize(700, 340)
        
        layout = QVBoxLayout(self.window)

        control_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear completed")
        self.clear_button.clicked.connect(self._clear_completed)
        control_layout.addWidget(self.clear_button)
        control_layout.addStretch(1)
        layout.addLayout(control_layout)

        self.table = QTableWidget(0, 4, self.window)
        self.table.setHorizontalHeaderLabels(["Filename", "Status", "Progress", "Location"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.window.setLayout(layout)

    def show_window(self):
        # 2. Show as a pop-up window on top
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def handle_download(self, download: QWebEngineDownloadRequest):
        row = self.table.rowCount()
        self.table.insertRow(row)
        filename = Path(download.downloadFileName() or download.url().fileName()).name or "download"
        self.table.setItem(row, 0, QTableWidgetItem(filename))
        self.table.setItem(row, 1, QTableWidgetItem("Starting"))
        self.table.setItem(row, 2, QTableWidgetItem("0%"))
        self.table.setItem(row, 3, QTableWidgetItem(download.downloadDirectory() or ""))

        download.receivedBytesChanged.connect(lambda _: self._update_progress(row, download))
        download.totalBytesChanged.connect(lambda _: self._update_progress(row, download))
        download.stateChanged.connect(lambda _: self._finish_download(row, download))
        download.accept()

    def _update_progress(self, row: int, download: QWebEngineDownloadRequest):
        received = download.receivedBytes()
        total = download.totalBytes()
        percent = 0 if total == 0 else int(received * 100 / total)
        self.table.setItem(row, 2, QTableWidgetItem(f"{percent}%"))

    def _finish_download(self, row: int, download: QWebEngineDownloadRequest):
        state = download.state()
        status = "Complete" if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted else "Canceled"
        self.table.setItem(row, 1, QTableWidgetItem(status))
        self.table.setItem(row, 2, QTableWidgetItem("100%" if status == "Complete" else "0%"))

    def _clear_completed(self):
        for index in reversed(range(self.table.rowCount())):
            status_item = self.table.item(index, 1)
            if status_item and status_item.text() == "Complete":
                self.table.removeRow(index)