# Plus Browser

- open source
- no bloat
- no data collection 
- full anti tracking protection

## Structure
- `main.py` — application entrypoint
- `browser.py` — main browser window
- `tab.py` — browser tab wrapper
- `bookmarks.py` — bookmark manager
- `history.py` — history database manager
- `downloads.py` — download panel and handler
- `settings.py` — JSON-backed settings loader
- `shortcuts.py` — keyboard shortcut wiring
- `ui/` — toolbar, sidebar, tabs, theme modules
- `assets/` — theme and icon assets
- `data/` — bookmarks and settings data files

## Installation

Create venv , then install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Requirements 

- `Memory per tab :` 10mb - 200mb 
-- depending on the website
- `Cpu :` 2 cores / 2 threads **(recommended)**
