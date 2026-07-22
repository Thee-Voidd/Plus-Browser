from PyQt6.QtWebEngineCore import QWebEngineSettings


def setup_profile(profile):

    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    profile.setHttpAcceptLanguage(
        "en-US,en;q=0.9"
    )

    settings = profile.settings()

    settings.setAttribute(
        QWebEngineSettings.WebAttribute.WebGLEnabled,
        True
    )

    settings.setAttribute(
        QWebEngineSettings.WebAttribute.PluginsEnabled,
        False
    )

    settings.setAttribute(
        QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,
        False
    )

    settings.setAttribute(
        QWebEngineSettings.WebAttribute.HyperlinkAuditingEnabled,
        False
    )