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

        function getCanvas() {
          return document.querySelector('canvas') || document.getElementById('wordcraft_canvas');
        }
        function getInput() {
          return document.querySelector('input');
        }

        // Lock inputmode to "none" so Chromium Android NEVER pops up the virtual keyboard on touch/scroll/selection
        function lockInputMode() {
          const inp = getInput();
          if (inp && !window.__softKeyboardRequested) {
            if (inp.getAttribute('inputmode') !== 'none') {
              inp.setAttribute('inputmode', 'none');
            }
          }
        }

        const observer = new MutationObserver(function() {
          lockInputMode();
        });
        observer.observe(document.documentElement || document.body, { childList: true, subtree: true });
        setInterval(lockInputMode, 200);

        window.__showKeyboard = function() {
          window.__softKeyboardRequested = true;
          const inp = getInput();
          if (inp) {
            inp.setAttribute('inputmode', 'text');
            try { inp.focus({ preventScroll: true }); } catch (e) { inp.focus(); }
          }
        };

        window.__hideKeyboard = function() {
          window.__softKeyboardRequested = false;
          const inp = getInput();
          if (inp) {
            inp.setAttribute('inputmode', 'none');
            try { inp.blur(); } catch (e) {}
          }
          const cvs = getCanvas();
          if (cvs) {
            try { cvs.focus({ preventScroll: true }); } catch (e) {}
          }
        };

        window.__onKeyboardHidden = function() {
          window.__softKeyboardRequested = false;
          const inp = getInput();
          if (inp) {
            inp.setAttribute('inputmode', 'none');
          }
        };

        // 3. Stationary double-tap only (ignores scroll and text-selection drag)
        let touchStartX = 0;
        let touchStartY = 0;
        let touchMoved = false;
        let lastTapTime = 0;

        window.addEventListener('touchstart', function(e) {
          if (e.touches.length === 1) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            touchMoved = false;
          }
        }, { passive: true });

        window.addEventListener('touchmove', function(e) {
          if (e.touches.length > 0) {
            const dx = Math.abs(e.touches[0].clientX - touchStartX);
            const dy = Math.abs(e.touches[0].clientY - touchStartY);
            if (dx > 10 || dy > 10) {
              touchMoved = true;
            }
          }
        }, { passive: true });

        window.addEventListener('touchend', function(e) {
          if (touchMoved) return; // Ignore drag / scroll / selection
          const now = Date.now();
          if (now - lastTapTime < 350) {
            if (window.__showKeyboard) window.__showKeyboard();
            if (window.AndroidBridge && window.AndroidBridge.showKeyboard) {
              window.AndroidBridge.showKeyboard();
            }
          }
          lastTapTime = now;
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
