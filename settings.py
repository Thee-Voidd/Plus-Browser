import json
from pathlib import Path


class SettingsManager:
    DEFAULTS = {
        "homepage": "https://www.google.com",
        "search_engine": "https://www.google.com/search?q={}",
        "downloads_folder": "",
        "theme": "dark",
        "accent_color": "#5a2db7",
    }

    def __init__(self, path: Path = Path("data/settings.json")):
        self.path = Path(path)
        self._data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                return {**self.DEFAULTS, **data}
            except Exception:
                pass

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.DEFAULTS, indent=2), encoding="utf-8")
        return dict(self.DEFAULTS)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    @property
    def homepage(self):
        return self._data.get("homepage", self.DEFAULTS["homepage"])

    @property
    def search_engine(self):
        return self._data.get("search_engine", self.DEFAULTS["search_engine"])

    @property
    def accent_color(self):
        return self._data.get("accent_color", self.DEFAULTS["accent_color"])
