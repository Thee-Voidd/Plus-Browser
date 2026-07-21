import json
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)


class BookmarkManager:
    def __init__(self, path: Path = Path("data/bookmarks.json")):
        self.path = Path(path)
        self.folders = {
            "toolbar": [],
            "programming": [],
            "school": [],
            "favorites": [],
        }
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                self.folders.update(loaded)
            except Exception:
                self._save()
        else:
            self._save()

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.folders, indent=2), encoding="utf-8")

    def add_bookmark(self, title: str, url: str, folder: str = "toolbar"):
        folder = folder if folder in self.folders else "toolbar"
        bookmark = {"title": title, "url": url}
        self.folders[folder].append(bookmark)
        self._save()

    def remove_bookmark(self, folder: str, index: int):
        if folder in self.folders and 0 <= index < len(self.folders[folder]):
            del self.folders[folder][index]
            self._save()

    def get_menu(self, parent, open_callback):
        menu = QMenu("Bookmarks", parent)
        for folder_name, entries in self.folders.items():
            if folder_name == "toolbar":
                for entry in entries:
                    action = menu.addAction(entry["title"])
                    action.triggered.connect(lambda checked, u=entry["url"]: open_callback(u))
            else:
                submenu = menu.addMenu(folder_name.title())
                for entry in entries:
                    action = submenu.addAction(entry["title"])
                    action.triggered.connect(lambda checked, u=entry["url"]: open_callback(u))
        return menu


class BookmarksDialog(QDialog):
    def __init__(self, manager: BookmarkManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Bookmarks")
        self.resize(760, 420)

        layout = QVBoxLayout(self)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Bookmarks", self))
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search bookmarks")
        self.search_input.textChanged.connect(self.update_bookmarks)
        header_layout.addWidget(self.search_input)
        layout.addLayout(header_layout)

        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["Title", "URL", "Folder"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)
        self.table.cellDoubleClicked.connect(self._open_selected_entry)
        layout.addWidget(self.table)

        self.update_bookmarks()

    def update_bookmarks(self):
        filter_text = self.search_input.text().lower().strip()
        self.table.setRowCount(0)
        for folder_name, entries in self.manager.folders.items():
            for index, entry in enumerate(entries):
                title = entry.get("title") or entry.get("url")
                url = entry.get("url")
                if filter_text and filter_text not in title.lower() and filter_text not in url.lower():
                    continue
                row = self.table.rowCount()
                self.table.insertRow(row)

                title_item = QTableWidgetItem(title)
                title_item.setData(Qt.ItemDataRole.UserRole, (folder_name, index))
                self.table.setItem(row, 0, title_item)
                self.table.setItem(row, 1, QTableWidgetItem(url))
                self.table.setItem(row, 2, QTableWidgetItem(folder_name.title()))

    def _open_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        selected = menu.exec(self.table.viewport().mapToGlobal(pos))
        if selected == delete_action:
            self._delete_bookmark(row)

    def _delete_bookmark(self, row: int):
        item = self.table.item(row, 0)
        if not item:
            return

        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        folder_name, index = data
        self.manager.remove_bookmark(folder_name, index)
        self.update_bookmarks()

    def _open_selected_entry(self, row: int, _column: int):
        url_item = self.table.item(row, 1)
        if url_item and self.parent() and hasattr(self.parent(), "open_tab"):
            self.parent().open_tab(url_item.text())
            self.close()
