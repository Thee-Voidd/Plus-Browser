import os
import urllib.request
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor


OISD_URL = "https://small.oisd.nl"
EASYPRIVACY_URL = "https://easylist.to/easylist/easyprivacy.txt"
OISD_FILE = "filters/oisd_small.txt"
EASYPRIVACY_FILE = "filters/easyprivacy.txt"


class AdBlocker(QWebEngineUrlRequestInterceptor):

    def __init__(self):
        super().__init__()

        self.enabled = True
        self.rules = set()

        os.makedirs("filters", exist_ok=True)

        self.download_filters()
        self.load_filters()

    def download_filter(self, url, filename):

        try:
            print(f"Updating {filename}...")

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
            }
        )

            with urllib.request.urlopen(request) as response:
                 data = response.read()

            with open(filename, "wb") as file:
                 file.write(data)

            print(f"{filename} updated")

        except Exception as e:
             print(
                     f"{filename} update failed:",
                     e
        )

    def download_filters(self):

        self.download_filter(
            OISD_URL,
            OISD_FILE
        )

        self.download_filter(
            EASYPRIVACY_URL,
            EASYPRIVACY_FILE
        )


    def load_filters(self):

        files = [
            OISD_FILE,
            EASYPRIVACY_FILE
        ]

        for filename in files:

            if not os.path.exists(filename):
                continue

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    line = line.strip()

                    # skip empty
                    if not line:
                        continue

                    # skip comments
                    if line.startswith("!"):
                         continue

                    if line.startswith("["):
                            continue

                    if line.startswith("@@"):
                        continue
                    if "##" in line:
                         continue
                    line = line.split("$")[0].strip()

                    # remove unsupported modifiers
                    if line.endswith("^"):
                      line = line[:-1]

                    self.rules.add(line)


        print(
            f"Loaded {len(self.rules)} rules"
        )


    def interceptRequest(self, info):

        if not self.enabled:
         return

        url = info.requestUrl().toString()
        for rule in self.rules:

            # domain rules
            if rule.startswith("||"):

                
                domain = rule[2:].split("^")[0]

                if domain and domain in url:

                    print("Blocked:", domain)
                    info.block(True)
                    return


            # path rules from EasyPrivacy
            elif rule.startswith("/"):

                path = rule

                if path in url:

                    print("Blocked:", path)
                    info.block(True)
                    return