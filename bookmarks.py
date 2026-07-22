import sqlite3
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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
    QInputDialog,
)


class BookmarkManager:
    def __init__(self, path: Path = Path("data/bookmarks.db")):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def add_bookmark(self, title: str = "", url: str = ""):
        if not title and not url:
            return

        if title.startswith(("http://", "https://", "file://", "about:")) and not url.startswith(("http://", "https://", "file://", "about:")):
            title, url = url, title

        actual_url = url or title
        actual_title = title or url

        if not actual_url:
            return

        self.connection.execute(
            "INSERT OR REPLACE INTO bookmarks (url, title, created_at) VALUES (?, ?, ?)",
            (actual_url, actual_title, datetime.utcnow().isoformat()),
        )
        self.connection.commit()

    def update_title(self, bookmark_id: int, new_title: str):
        self.connection.execute(
            "UPDATE bookmarks SET title = ? WHERE id = ?",
            (new_title, bookmark_id),
        )
        self.connection.commit()

    def delete_bookmark(self, bookmark_id: int):
        self.connection.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        self.connection.commit()

    def all_items(self):
        cursor = self.connection.execute(
            "SELECT id, url, title, created_at FROM bookmarks ORDER BY id DESC"
        )
        return cursor.fetchall()


class BookmarksDialog(QDialog):
    def __init__(self, manager: BookmarkManager = None, open_callback=None, parent=None):
        super().__init__(parent)
        self.manager = manager or BookmarkManager()
        self.open_callback = open_callback
        self.setWindowTitle("Bookmarks")
        self.resize(780, 420)

        # منع الخط المايل في شباك البوك مارك بالكامل
        base_font = self.font()
        base_font.setItalic(False)
        self.setFont(base_font)

        # إجبار جميع الأزرار والـ Elements على منع الـ Italic عن طريق QSS
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
        top_row.addWidget(QLabel("Search bookmarks:", self))
        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText("Search by title or URL")
        self.filter_input.textChanged.connect(self.update_bookmarks)
        top_row.addWidget(self.filter_input)
        layout.addLayout(top_row)

        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["Title", "URL", "Added"])
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

        self.rename_btn = QPushButton("Rename", self)
        self.rename_btn.clicked.connect(self._rename_current_selection)
        btn_row.addWidget(self.rename_btn)

        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.clicked.connect(self._delete_current_selection)
        btn_row.addWidget(self.delete_btn)

        layout.addLayout(btn_row)

        self.update_bookmarks()

    def update_bookmarks(self):
        term = self.filter_input.text().lower().strip() if hasattr(self, "filter_input") else ""
        self.table.setRowCount(0)
        for bookmark_id, url, title, created_at in self.manager.all_items():
            if term and term not in url.lower() and term not in (title or "").lower():
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)

            title_item = QTableWidgetItem(title or url)
            title_item.setData(Qt.ItemDataRole.UserRole, bookmark_id)

            self.table.setItem(row, 0, title_item)
            self.table.setItem(row, 1, QTableWidgetItem(url))
            self.table.setItem(row, 2, QTableWidgetItem(created_at))

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return

        row = item.row()
        self.table.selectRow(row)

        menu = QMenu(self)
        open_action = menu.addAction("Open in New Tab")
        rename_action = menu.addAction("Rename Bookmark")
        delete_action = menu.addAction("Delete Bookmark")

        selected = menu.exec(self.table.viewport().mapToGlobal(pos))
        if selected == open_action:
            self._open_selected_entry(row, 1)
        elif selected == rename_action:
            self._rename_bookmark(row)
        elif selected == delete_action:
            self._delete_bookmark(row)

    def _rename_current_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            self._rename_bookmark(row)

    def _delete_current_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            self._delete_bookmark(row)

    def _rename_bookmark(self, row: int):
        title_item = self.table.item(row, 0)
        if not title_item:
            return

        bookmark_id = title_item.data(Qt.ItemDataRole.UserRole)
        current_title = title_item.text()

        new_title, ok = QInputDialog.getText(
            self, "Rename Bookmark", "Enter new title:", QLineEdit.EchoMode.Normal, current_title
        )
        if ok and new_title.strip():
            self.manager.update_title(bookmark_id, new_title.strip())
            self.update_bookmarks()

    def _delete_bookmark(self, row: int):
        title_item = self.table.item(row, 0)
        if title_item:
            bookmark_id = title_item.data(Qt.ItemDataRole.UserRole)
            if bookmark_id is not None:
                self.manager.delete_bookmark(bookmark_id)
                self.update_bookmarks()

    def _open_selected_entry(self, row, _column):
        url_item = self.table.item(row, 1)
        if url_item:
            url = url_item.text()
            if callable(self.open_callback):
                self.open_callback(url)
            elif self.parent() and hasattr(self.parent(), "open_tab"):
                self.parent().open_tab(url)
            self.close()