import sqlite3
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QMenu,
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

    def delete_entry(self, history_id: int):
        self.connection.execute("DELETE FROM history WHERE id = ?", (history_id,))
        self.connection.commit()

    def recent_items(self, limit: int = 200):
        cursor = self.connection.execute(
            "SELECT id, url, title, visited_at FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cursor.fetchall()


class HistoryDialog(QDialog):
    def __init__(self, manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("History")
        self.resize(780, 420)

        # منع الخط المايل في شباك السجل بالكامل
        base_font = self.font()
        base_font.setItalic(False)
        self.setFont(base_font)

        # إجبار العناصر والأزرار على الخط العادي
        self.setStyleSheet("""
            QWidget {
                font-style: normal;
            }
            QPushButton {
                font-style: normal;
                font-weight: normal;
                padding: 6px 14px;
            }
        """)

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

        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        self.table.cellDoubleClicked.connect(self._open_selected_entry)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.clicked.connect(self._delete_current_selection)
        btn_row.addWidget(self.delete_btn)
        layout.addLayout(btn_row)

        self.update_history()

    def update_history(self):
        term = self.filter_input.text().lower().strip()
        self.table.setRowCount(0)
        for history_id, url, title, visited in self.manager.recent_items(200):
            if term and term not in url.lower() and term not in (title or "").lower():
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)

            title_item = QTableWidgetItem(title or url)
            title_item.setData(Qt.ItemDataRole.UserRole, history_id)

            self.table.setItem(row, 0, title_item)
            self.table.setItem(row, 1, QTableWidgetItem(url))
            self.table.setItem(row, 2, QTableWidgetItem(visited))

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return

        row = item.row()
        self.table.selectRow(row)

        menu = QMenu(self)
        open_action = menu.addAction("Open in New Tab")
        delete_action = menu.addAction("Delete History Entry")

        selected = menu.exec(self.table.viewport().mapToGlobal(pos))
        if selected == open_action:
            self._open_selected_entry(row, 1)
        elif selected == delete_action:
            self._delete_history_entry(row)

    def _delete_current_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            self._delete_history_entry(row)

    def _delete_history_entry(self, row: int):
        title_item = self.table.item(row, 0)
        if title_item:
            history_id = title_item.data(Qt.ItemDataRole.UserRole)
            if history_id is not None:
                self.manager.delete_entry(history_id)
                self.update_history()

    def _open_selected_entry(self, row, _column):
        url_item = self.table.item(row, 1)
        if url_item:
            url = url_item.text()
            if self.parent() and hasattr(self.parent(), "open_tab"):
                self.parent().open_tab(url)
            self.close()