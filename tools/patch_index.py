#!/usr/bin/env python3
import sys
import re

BRIDGE_AND_FONT_SNIPPET = """  <script>
    // AndroidBridge file save & virtual keyboard integration
    (function() {
      function setupBridge() {
        if (!window.AndroidBridge) return;

        // 1. Intercept file downloads via blob links
        const origClick = HTMLAnchorElement.prototype.click;
        HTMLAnchorElement.prototype.click = function() {
          if (this.download && this.href && this.href.startsWith("blob:")) {
            const filename = this.download;
            fetch(this.href)
              .then(res => res.blob())
              .then(blob => {
                const reader = new FileReader();
                reader.onloadend = function() {
                  const base64 = reader.result.split(',')[1];
                  window.AndroidBridge.saveFile(base64, filename, blob.type || "application/octet-stream");
                };
                reader.readAsDataURL(blob);
              })
              .catch(err => console.error("Error in AndroidBridge download:", err));
            return;
          }
          return origClick.apply(this, arguments);
        };

        // 2. Auto-forward eframe text input focus to Android soft keyboard
        document.addEventListener('focusin', function(e) {
          if (e.target && e.target.tagName === 'INPUT') {
            if (window.AndroidBridge && window.AndroidBridge.showKeyboard) {
              window.AndroidBridge.showKeyboard();
            }
          }
        }, true);

        document.addEventListener('focusout', function(e) {
          if (e.target && e.target.tagName === 'INPUT') {
            if (window.AndroidBridge && window.AndroidBridge.hideKeyboard) {
              window.AndroidBridge.hideKeyboard();
            }
          }
        }, true);

        // 3. Double-tap on canvas to focus input and trigger soft keyboard
        let lastTap = 0;
        window.addEventListener('touchend', function(e) {
          const now = Date.now();
          if (now - lastTap < 350) {
            const inp = document.querySelector('input');
            if (inp) {
              try { inp.focus({ preventScroll: true }); } catch (err) { inp.focus(); }
            }
            if (window.AndroidBridge && window.AndroidBridge.showKeyboard) {
              window.AndroidBridge.showKeyboard();
            }
          }
          lastTap = now;
        }, { passive: true });
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupBridge);
      } else {
        setupBridge();
      }
    })();

    // Preload Office font pack into WordCraft IndexedDB
    (function() {
      const FONTS = [
        "Arial.ttf", "Arial_Bold.ttf", "Arial_Italic.ttf",
        "Times_New_Roman.ttf", "Times_New_Roman_Bold.ttf", "Times_New_Roman_Italic.ttf",
        "Calibri.ttf", "Calibri_Bold.ttf",
        "Carlito-Regular.ttf", "Caladea-Regular.ttf",
        "Courier_New.ttf", "Courier_New_Bold.ttf",
        "Comic_Sans_MS.ttf", "Comic_Sans_MS_Bold.ttf",
        "Georgia.ttf", "Georgia_Bold.ttf",
        "Verdana.ttf", "Verdana_Bold.ttf",
        "Trebuchet_MS.ttf", "Trebuchet_MS_Bold.ttf",
        "Roboto.ttf", "Roboto-Italic.ttf"
      ];

      function preload() {
        return new Promise(function(resolve) {
          if (!window.indexedDB) { resolve(); return; }
          const req = indexedDB.open("wordcraft");
          req.onupgradeneeded = function(e) {
            const db = e.target.result;
            if (!db.objectStoreNames.contains("fonts")) {
              db.createObjectStore("fonts");
            }
          };
          req.onsuccess = function(e) {
            const db = e.target.result;
            if (!db.objectStoreNames.contains("fonts")) {
              resolve();
              return;
            }
            try {
              const tx = db.transaction("fonts", "readonly");
              const store = tx.objectStore("fonts");
              const getKeys = store.getAllKeys();
              getKeys.onsuccess = async function() {
                const existing = new Set(getKeys.result || []);
                const missing = FONTS.filter(f => !existing.has(f));
                if (missing.length === 0) {
                  resolve();
                  return;
                }
                console.log("Preloading " + missing.length + " Office fonts into IndexedDB...");
                const fetches = missing.map(async function(f) {
                  try {
                    const res = await fetch("./fonts/" + f);
                    if (res.ok) {
                      const buf = await res.arrayBuffer();
                      return { name: f, data: new Uint8Array(buf) };
                    }
                  } catch (err) {}
                  return null;
                });
                const loaded = (await Promise.all(fetches)).filter(Boolean);
                if (loaded.length > 0) {
                  const wtx = db.transaction("fonts", "readwrite");
                  const wStore = wtx.objectStore("fonts");
                  for (const item of loaded) {
                    wStore.put(item.data, item.name);
                  }
                  await new Promise(function(r) {
                    wtx.oncomplete = r;
                    wtx.onerror = r;
                  });
                }
                resolve();
              };
              getKeys.onerror = function() { resolve(); };
            } catch (err) {
              resolve();
            }
          };
          req.onerror = function() { resolve(); };
        });
      }

      window.preloadFontsPromise = Promise.race([
        preload(),
        new Promise(function(r) { setTimeout(r, 5000); })
      ]);
    })();
  </script>"""

def main():
    if len(sys.argv) < 2:
        print("Usage: patch_index.py <path/to/index.html>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Insert Bridge & Font Preload script into <head>
    if "Preload Office font pack into WordCraft IndexedDB" not in content:
        if "</head>" in content:
            content = content.replace("</head>", BRIDGE_AND_FONT_SNIPPET + "\n</head>")
        else:
            content = BRIDGE_AND_FONT_SNIPPET + "\n" + content

    # 2. Await font preload before WASM initialization
    if "await window.preloadFontsPromise" not in content:
        pattern = r'(const\s+wasm\s*=\s*await\s+init)'
        replacement = r'''if (window.preloadFontsPromise) {
  try { await window.preloadFontsPromise; } catch (e) { console.warn('Preload font error:', e); }
}
\1'''
        content = re.sub(pattern, replacement, content, count=1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched index.html with AndroidBridge and Font Preloader")

if __name__ == "__main__":
    main()
