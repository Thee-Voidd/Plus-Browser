import sqlite3
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QHBoxLayout,
)


class HistoryManager:
    def __init__(self, path: Path = Path("data/history.db")):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                visited_at TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def add_entry(self, url: str, title: str):
        if not url:
            return
        self.connection.execute(
            "INSERT INTO history (url, title, visited_at) VALUES (?, ?, ?)",
            (url, title or url, datetime.utcnow().isoformat()),
        )
        self.connection.commit()

    def recent_items(self, limit: int = 20):
        cursor = self.connection.execute(
            "SELECT url, title, visited_at FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cursor.fetchall()


class HistoryDialog(QDialog):
    def __init__(self, manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("History")
        self.resize(780, 420)

        layout = QVBoxLayout(self)
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Search history:", self))
        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText("Search by title or URL")
        self.filter_input.textChanged.connect(self.update_history)
        top_row.addWidget(self.filter_input)
        layout.addLayout(top_row)

        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["Title", "URL", "Visited"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._open_selected_entry)
        layout.addWidget(self.table)

        self.update_history()

    def update_history(self):
        term = self.filter_input.text().lower().strip()
        self.table.setRowCount(0)
        for url, title, visited in self.manager.recent_items(200):
            if term and term not in url.lower() and term not in (title or "").lower():
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(title or url))
            self.table.setItem(row, 1, QTableWidgetItem(url))
            self.table.setItem(row, 2, QTableWidgetItem(visited))

    def _open_selected_entry(self, row, _column):
        url_item = self.table.item(row, 1)
        if url_item:
            url = url_item.text()
            if self.parent() and hasattr(self.parent(), "open_tab"):
                self.parent().open_tab(url)
            self.close()
