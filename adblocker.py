import os
import urllib.request
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo

OISD_URL = "https://small.oisd.nl"
EASYPRIVACY_URL = "https://easylist.to/easylist/easyprivacy.txt"
OISD_FILE = "filters/oisd_small.txt"
EASYPRIVACY_FILE = "filters/easyprivacy.txt"

# Whitelist functional infrastructure domains
WHITELIST_DOMAINS = {
    "googlevideo.com",
    "ytimg.com",
    "youtube.com",
    "fonts.googleapis.com",
    "ajax.googleapis.com",
    "gstatic.com"
}

class AdBlocker(QWebEngineUrlRequestInterceptor):

    def __init__(self):
        super().__init__()

        self.enabled = True
        self.blocked_domains = set()  # Fast O(1) exact/suffix lookup
        self.blocked_paths = tuple()  # Efficient tuple for fast endswith/in checks

        os.makedirs("filters", exist_ok=True)

        self.download_filters()
        self.load_filters()

    def download_filter(self, url, filename):
        try:
            print(f"Updating {filename}...")
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request) as response:
                data = response.read()
            with open(filename, "wb") as file:
                file.write(data)
            print(f"{filename} updated")
        except Exception as e:
            print(f"{filename} update failed:", e)

    def download_filters(self):
        self.download_filter(OISD_URL, OISD_FILE)
        self.download_filter(EASYPRIVACY_URL, EASYPRIVACY_FILE)

    def load_filters(self):
        domains = set()
        paths = []

        files = [OISD_FILE, EASYPRIVACY_FILE]

        for filename in files:
            if not os.path.exists(filename):
                continue

            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    # Skip empty lines, comments, and complex elements
                    if not line or line.startswith(("!", "[", "@@")) or "##" in line:
                        continue

                    # Strip options/modifiers
                    line = line.split("$")[0].strip()
                    if line.endswith("^"):
                        line = line[:-1]

                    # Parse domain rules (e.g. ||example.com)
                    if line.startswith("||"):
                        domain = line[2:].split("^")[0].lower()
                        if domain and domain not in WHITELIST_DOMAINS:
                            domains.add(domain)

                    # Parse path/string rules
                    elif line.startswith("/") and len(line) > 3:
                        paths.append(line.lower())

        self.blocked_domains = domains
        self.blocked_paths = tuple(paths)

        print(f"Loaded {len(self.blocked_domains)} blocked domains & {len(self.blocked_paths)} paths")

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        if not self.enabled:
            return

        # 1. Do not block main page navigation
        if info.resourceType() == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
            return

        req_url = info.requestUrl()
        host = req_url.host().lower()

        # 2. Skip whitelisted infrastructure domains instantly
        if any(host == w or host.endswith("." + w) for w in WHITELIST_DOMAINS):
            return

        # 3. Fast O(1) Domain Check (Matches domain or parent domain)
        parts = host.split('.')
        for i in range(len(parts) - 1):
            subdomain = ".".join(parts[i:])
            if subdomain in self.blocked_domains:
                info.block(True)
                return

        # 4. Path Check (Only checked if domain isn't whitelisted)
        url_str = req_url.toString().lower()
        if any(path in url_str for path in self.blocked_paths):
            info.block(True)