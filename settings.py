import json
from pathlib import Path


class SettingsManager:

    DEFAULTS = {

        "homepage": "https://www.google.com",

        "search_engine": 
            "https://www.google.com/search?q={}",

        "downloads_folder": "",

        "theme": "dark",

        "accent_color": "#5a2db7",

        "privacy": {

            "block_trackers": True,

            "block_third_party_cookies": True,

            "disable_webrtc": True,

            "fingerprint_protection": True

        }

    }


    def __init__(
        self,
        path: Path = Path("data/settings.json")
    ):

        self.path = Path(path)

        self._data = self._load()



    def _load(self):

        if self.path.exists():

            try:

                data = json.loads(
                    self.path.read_text(
                        encoding="utf-8"
                    )
                )

                return self.merge_defaults(
                    data
                )

            except Exception:

                pass


        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        self.path.write_text(
            json.dumps(
                self.DEFAULTS,
                indent=4
            ),
            encoding="utf-8"
        )


        return dict(self.DEFAULTS)



    def merge_defaults(self, data):

        result = dict(self.DEFAULTS)

        for key, value in data.items():

            if isinstance(value, dict) and key in result:

                result[key].update(value)

            else:

                result[key] = value

        return result



    def save(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.path.write_text(
            json.dumps(
                self._data,
                indent=4
            ),
            encoding="utf-8"
        )



    # ---------- Browser ----------

    @property
    def homepage(self):

        return self._data["homepage"]



    @homepage.setter
    def homepage(self, value):

        self._data["homepage"] = value



    @property
    def search_engine(self):

        return self._data["search_engine"]



    @property
    def downloads_folder(self):

        return self._data["downloads_folder"]



    # ---------- Appearance ----------

    @property
    def theme(self):

        return self._data["theme"]



    @theme.setter
    def theme(self, value):

        self._data["theme"] = value



    @property
    def accent_color(self):

        return self._data["accent_color"]



    @accent_color.setter
    def accent_color(self, value):

        self._data["accent_color"] = value



    # ---------- Privacy ----------

    @property
    def privacy(self):

        return self._data["privacy"]