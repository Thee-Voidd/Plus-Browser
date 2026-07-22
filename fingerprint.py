from PyQt6.QtWebEngineCore import QWebEngineScript


def install_fingerprint_protection(profile):

    script = QWebEngineScript()

    script.setName("fingerprint_protection")

    script.setInjectionPoint(
        QWebEngineScript.InjectionPoint.DocumentCreation
    )

    script.setWorldId(
        QWebEngineScript.ScriptWorldId.MainWorld
    )

    script.setSourceCode("""
    
    // Canvas read protection
    const originalDataURL =
        HTMLCanvasElement.prototype.toDataURL;

    HTMLCanvasElement.prototype.toDataURL = function() {

        const ctx = this.getContext("2d");

        if (ctx) {
            const imageData = ctx.getImageData(
                0,
                0,
                this.width,
                this.height
            );

            for(let i = 0; i < imageData.data.length; i += 4){
                imageData.data[i] ^= 1;
            }

            ctx.putImageData(
                imageData,
                0,
                0
            );
        }

        return originalDataURL.apply(this, arguments);
    };


    // WebRTC protection
    if (navigator.mediaDevices) {
        Object.defineProperty(
            navigator,
            "mediaDevices",
            {
                get: () => undefined
            }
        );
    }


    """)

    profile.scripts().insert(script)