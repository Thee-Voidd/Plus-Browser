import sqlite3
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHeaderView,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class DownloadsManager:

    def __init__(
        self, parent=None, db_path: Path = Path("data/downloads.db")
    ):
        self.parent = parent
        self.downloads = []  # Active QWebEngineDownloadRequest instances

        # --- SQLite Database Setup ---
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(
            str(self.db_path), check_same_thread=False
        )
        self._create_tables()

        # --- UI Dialog Setup ---
        self.window = QDialog(parent)
        self.window.setWindowTitle("Downloads")
        self.window.resize(750, 350)

        layout = QVBoxLayout(self.window)
        self.table = QTableWidget(0, 7, self.window)
        self.table.setHorizontalHeaderLabels(
            [
                "Filename",
                "Status",
                "Progress",
                "Pause",
                "Cancel",
                "Open",
                "Folder",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Load historical downloads from database on startup
        self.load_history_from_db()

    # --- Database Operations ---

    def _create_tables(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def add_db_entry(self, filename: str, file_path: str, url: str) -> int:
        cursor = self.connection.execute(
            "INSERT INTO downloads (filename, file_path, url, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                filename,
                file_path,
                url,
                "Downloading",
                datetime.utcnow().isoformat(),
            ),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_db_status(self, db_id: int, status: str):
        self.connection.execute(
            "UPDATE downloads SET status = ? WHERE id = ?", (status, db_id)
        )
        self.connection.commit()

    # --- Stylesheets ---

    @property
    def active_btn_style(self):
        return """
            QPushButton {
                background-color: #181a20;
                color: white;
                border-radius: 0px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.08);
            }
        """

    @property
    def active_cancel_style(self):
        return """
            QPushButton {
                background-color: #181a20;
                color: white;
                border-radius: 0px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.08);
                color: white;
            }
        """

    @property
    def disabled_btn_style(self):
        return """
            QPushButton {
                border-radius: 0px;
                background-color: #252832;
                color:  #808080;
                padding: 4px 8px;
            }
        """

    # --- Methods ---

    def show_window(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def load_history_from_db(self):
        """Populates the table with previously recorded downloads from SQLite."""
        cursor = self.connection.execute(
            "SELECT id, filename, file_path, status FROM downloads ORDER BY id ASC"
        )
        rows = cursor.fetchall()

        for db_id, filename, file_path, status in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)

            path = Path(file_path)

            self.table.setItem(row, 0, QTableWidgetItem(filename))
            self.table.setItem(row, 1, QTableWidgetItem(status))

            # Saved progress bar (100% for completed, 0% for cancelled/interrupted)
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(100 if status == "Completed" else 0)
            self.table.setCellWidget(row, 2, progress)

            # Historical items have finished downloading, so Pause & Cancel are disabled
            pause_btn = QPushButton("Pause")
            cancel_btn = QPushButton("Cancel")
            open_btn = QPushButton("Open")
            folder_btn = QPushButton("Folder")

            pause_btn.setStyleSheet(self.disabled_btn_style)
            cancel_btn.setStyleSheet(self.disabled_btn_style)
            pause_btn.setEnabled(False)
            cancel_btn.setEnabled(False)

            # Open/Folder buttons enabled only if completed and file exists
            if status == "Completed":
                open_btn.setStyleSheet(self.active_btn_style)
                folder_btn.setStyleSheet(self.active_btn_style)
                open_btn.setEnabled(True)
                folder_btn.setEnabled(True)

                open_btn.clicked.connect(
                    lambda checked=False, p=file_path: QDesktopServices.openUrl(
                        QUrl.fromLocalFile(p)
                    )
                )
                folder_btn.clicked.connect(
                    lambda checked=False, p=str(
                        path.parent
                    ): QDesktopServices.openUrl(QUrl.fromLocalFile(p))
                )
            else:
                open_btn.setStyleSheet(self.disabled_btn_style)
                folder_btn.setStyleSheet(self.disabled_btn_style)
                open_btn.setEnabled(False)
                folder_btn.setEnabled(False)

            self.table.setCellWidget(row, 3, pause_btn)
            self.table.setCellWidget(row, 4, cancel_btn)
            self.table.setCellWidget(row, 5, open_btn)
            self.table.setCellWidget(row, 6, folder_btn)

    def handle_download(self, download: QWebEngineDownloadRequest):
        default_name = (
            Path(download.downloadFileName()).name
            or download.url().fileName()
            or "download"
        )

        filename, _ = QFileDialog.getSaveFileName(
            self.window, "Save File", default_name
        )

        if not filename:
            download.cancel()
            return

        path = Path(filename)

        download.setDownloadDirectory(str(path.parent))
        download.setDownloadFileName(path.name)
        download.local_path = str(path)

        # Record download in DB
        db_id = self.add_db_entry(
            path.name, str(path), download.url().toString()
        )

        self.downloads.append(download)

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(path.name))
        self.table.setItem(row, 1, QTableWidgetItem("Downloading"))

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        self.table.setCellWidget(row, 2, progress)

        pause_btn = QPushButton("Pause")
        cancel_btn = QPushButton("Cancel")
        open_btn = QPushButton("Open")
        folder_btn = QPushButton("Folder")

        # Set initial styles and states
        pause_btn.setStyleSheet(self.active_btn_style)
        cancel_btn.setStyleSheet(self.active_cancel_style)
        open_btn.setStyleSheet(self.disabled_btn_style)
        folder_btn.setStyleSheet(self.disabled_btn_style)

        open_btn.setEnabled(False)
        folder_btn.setEnabled(False)

        self.table.setCellWidget(row, 3, pause_btn)
        self.table.setCellWidget(row, 4, cancel_btn)
        self.table.setCellWidget(row, 5, open_btn)
        self.table.setCellWidget(row, 6, folder_btn)

        pause_btn.clicked.connect(
            lambda checked=False, d=download, b=pause_btn: self.pause_resume(
                d, b
            )
        )

        cancel_btn.clicked.connect(download.cancel)

        open_btn.clicked.connect(
            lambda checked=False,
            p=download.local_path: QDesktopServices.openUrl(
                QUrl.fromLocalFile(p)
            )
        )

        folder_btn.clicked.connect(
            lambda checked=False, p=str(path.parent): QDesktopServices.openUrl(
                QUrl.fromLocalFile(p)
            )
        )

        download.receivedBytesChanged.connect(
            lambda r=row, d=download: self.update_progress(r, d)
        )

        download.totalBytesChanged.connect(
            lambda r=row, d=download: self.update_progress(r, d)
        )

        download.stateChanged.connect(
            lambda state,
            r=row,
            d=download,
            p=pause_btn,
            c=cancel_btn,
            o=open_btn,
            f=folder_btn,
            i=db_id: self.update_state(
                r,
                d,
                p,
                c,
                o,
                f,
                i,
                self.active_btn_style,
                self.disabled_btn_style,
            )
        )

        download.accept()

    def update_progress(self, row: int, download: QWebEngineDownloadRequest):
        received = download.receivedBytes()
        total = download.totalBytes()
        if total > 0:
            percent = int((received / total) * 100)
            pbar = self.table.cellWidget(row, 2)
            if isinstance(pbar, QProgressBar):
                pbar.setValue(percent)

    def pause_resume(
        self, download: QWebEngineDownloadRequest, button: QPushButton
    ):
        if download.isPaused():
            download.resume()
            button.setText("Pause")
        else:
            download.pause()
            button.setText("Resume")

    def update_state(
        self,
        row: int,
        download: QWebEngineDownloadRequest,
        pause_btn: QPushButton,
        cancel_btn: QPushButton,
        open_btn: QPushButton,
        folder_btn: QPushButton,
        db_id: int,
        active_style: str,
        disabled_style: str,
    ):
        state = download.state()

        # Disable Pause & Cancel when done/interrupted/cancelled
        if state in (
            QWebEngineDownloadRequest.DownloadState.DownloadCompleted,
            QWebEngineDownloadRequest.DownloadState.DownloadCancelled,
            QWebEngineDownloadRequest.DownloadState.DownloadInterrupted,
        ):
            pause_btn.setEnabled(False)
            cancel_btn.setEnabled(False)
            pause_btn.setStyleSheet(disabled_style)
            cancel_btn.setStyleSheet(disabled_style)

        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.table.setItem(row, 1, QTableWidgetItem("Completed"))
            self.update_db_status(db_id, "Completed")

            # Enable action buttons
            open_btn.setEnabled(True)
            folder_btn.setEnabled(True)
            open_btn.setStyleSheet(active_style)
            folder_btn.setStyleSheet(active_style)

        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self.table.setItem(row, 1, QTableWidgetItem("Cancelled"))
            self.update_db_status(db_id, "Cancelled")

        elif (
            state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted
        ):
            self.table.setItem(row, 1, QTableWidgetItem("Interrupted"))
            self.update_db_status(db_id, "Interrupted")