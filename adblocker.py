from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor


class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()

        # This will store all blocked domains
        self.rules = set()

        # Loads the ad blocking list
        self.load_peter_lowe()

        print(f"Loaded {len(self.rules)} blocked domains.")

    def load_peter_lowe(self):
        try:
            with open("filters/peter_lowe.txt", "r", encoding="utf8") as file:
                for line in file:
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Skip comments
                    if line.startswith("#"):
                        continue

                    parts = line.split()

                   
                    # 127.0.0.1 ads.example.com
                    if len(parts) != 2:
                        continue

                    ip, host = parts

                    self.rules.add(host.lower())

        except FileNotFoundError:
            print("Could not find filters/peter_lowe.txt")

    def interceptRequest(self, info):
        host = info.requestUrl().host().lower()

        if host in self.rules:
            print("Blocked:", host)
            info.block(True)